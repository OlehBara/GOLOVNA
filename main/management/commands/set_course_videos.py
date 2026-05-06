from django.apps import apps
from django.core.management.base import BaseCommand

from main.models import Course


class Command(BaseCommand):
    help = "Прив'язує задані YouTube-відео до перших уроків конкретних курсів (лише зміна video_url, без зміни дизайну)."

    def handle(self, *args, **options):
        Lesson = apps.get_model("main", "Lesson")

        # Map: назва курсу -> YouTube watch URL
        course_videos = {
            "Основи бюджетування": "https://www.youtube.com/watch?v=UySfX5T9X3g",
            "Фінансове планування сім'ї": "https://www.youtube.com/watch?v=zEuiz1uorL0",
            "Фінансова грамотність для початківців": "https://www.youtube.com/watch?v=e4BthWshTCE",
        }

        def to_embed(url: str) -> str:
            """
            Перетворює стандартний YouTube watch URL у embed-формат,
            щоб його можна було вставити в iframe.
            """
            if "watch?v=" in url:
                video_id = url.split("watch?v=")[-1].split("&")[0]
                return f"https://www.youtube.com/embed/{video_id}"
            return url

        for title, watch_url in course_videos.items():
            try:
                course = Course.objects.get(title=title)
            except Course.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Курс з назвою '{title}' не знайдено. Пропускаю."
                    )
                )
                continue

            lesson = (
                Lesson.objects.filter(course=course).order_by("order", "id").first()
            )

            if not lesson:
                self.stdout.write(
                    self.style.WARNING(
                        f"Для курсу '{title}' ще немає уроків (Lesson). Пропускаю."
                    )
                )
                continue

            embed_url = to_embed(watch_url)
            lesson.video_url = embed_url
            lesson.save(update_fields=["video_url"])

            self.stdout.write(
                self.style.SUCCESS(
                    f"Оновлено video_url першого уроку курсу '{title}' -> {embed_url}"
                )
            )
