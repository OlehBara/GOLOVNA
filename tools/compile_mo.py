import os
import struct
import sys
from pathlib import Path


def parse_po(po_text: str):
    """
    Very small .po parser (enough for our simple catalog).
    Supports: msgid, msgstr, multi-line quoted strings.
    Ignores comments and plural forms.
    """
    entries = {}
    msgid = None
    msgstr = None
    mode = None

    def unquote(s: str) -> str:
        s = s.strip()
        if not (s.startswith('"') and s.endswith('"')):
            return ""
        return bytes(s[1:-1], "utf-8").decode("unicode_escape")

    def commit():
        nonlocal msgid, msgstr
        if msgid is not None and msgstr is not None:
            entries[msgid] = msgstr
        msgid = None
        msgstr = None

    for raw_line in po_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("msgid "):
            commit()
            mode = "msgid"
            msgid = unquote(line[len("msgid ") :])
            msgstr = None
            continue

        if line.startswith("msgstr "):
            mode = "msgstr"
            msgstr = unquote(line[len("msgstr ") :])
            continue

        if line.startswith('"'):
            if mode == "msgid" and msgid is not None:
                msgid += unquote(line)
            elif mode == "msgstr" and msgstr is not None:
                msgstr += unquote(line)
            continue

        # ignore anything else (plural forms etc.)

    commit()
    return entries


def write_mo(entries: dict[str, str], out_path: Path):
    """
    Writes a minimal GNU .mo file.
    """
    # Sort by msgid for binary search lookup
    keys = sorted(entries.keys())
    offsets = []

    ids = b"\x00".join(k.encode("utf-8") for k in keys) + b"\x00"
    strs = b"\x00".join(entries[k].encode("utf-8") for k in keys) + b"\x00"

    # Header
    magic = 0x950412DE
    revision = 0
    n = len(keys)
    # Offsets will be placed after header + tables
    header_size = 7 * 4
    orig_table_offset = header_size
    trans_table_offset = orig_table_offset + n * 8
    string_data_offset = trans_table_offset + n * 8

    # Build tables
    orig_table = b""
    trans_table = b""

    o_offset = 0
    t_offset = 0
    for k in keys:
        k_bytes = k.encode("utf-8")
        v_bytes = entries[k].encode("utf-8")
        orig_table += struct.pack("II", len(k_bytes), string_data_offset + o_offset)
        trans_table += struct.pack(
            "II", len(v_bytes), string_data_offset + len(ids) + t_offset
        )
        o_offset += len(k_bytes) + 1
        t_offset += len(v_bytes) + 1

    data = ids + strs

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as f:
        f.write(struct.pack("I", magic))
        f.write(struct.pack("I", revision))
        f.write(struct.pack("I", n))
        f.write(struct.pack("I", orig_table_offset))
        f.write(struct.pack("I", trans_table_offset))
        f.write(struct.pack("I", 0))  # hash table size
        f.write(struct.pack("I", 0))  # hash table offset
        f.write(orig_table)
        f.write(trans_table)
        f.write(data)


def main():
    base = Path(__file__).resolve().parents[1]
    locale_dir = base / "locale"
    if not locale_dir.exists():
        print("No locale/ directory found.")
        return 1

    po_files = list(locale_dir.glob("*/LC_MESSAGES/django.po"))
    if not po_files:
        print("No django.po files found.")
        return 1

    for po in po_files:
        catalog = parse_po(po.read_text(encoding="utf-8"))
        mo_path = po.with_suffix(".mo")
        write_mo(catalog, mo_path)
        print(f"Wrote {mo_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
