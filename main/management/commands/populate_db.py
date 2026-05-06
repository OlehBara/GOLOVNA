"""
Django management command to populate the FinSmart database.

Usage:
    python manage.py populate_db
    python manage.py populate_db --clear   # wipe existing data first
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone


class Command(BaseCommand):
    help = "Populate the database with courses, subscription plans, and reviews"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing courses, subscription plans, and reviews before seeding",
        )

    def handle(self, *args, **options):
        # Import models here to avoid circular imports
        from main.models import Course, Review, SubscriptionPlan

        if options["clear"]:
            self.stdout.write("🗑️  Clearing existing data...")
            Review.objects.all().delete()
            Course.objects.all().delete()
            SubscriptionPlan.objects.all().delete()
            self.stdout.write(self.style.WARNING("   Cleared courses, reviews, subscriptions."))

        # ── 1. Subscription Plans ────────────────────────────────────────────
        self.stdout.write("\n📦 Creating subscription plans...")
        plans_data = [
            {"name": "standard", "price": "299.00", "duration_days": 30},
            {"name": "family",   "price": "499.00", "duration_days": 30},
            {"name": "student",  "price": "149.00", "duration_days": 30},
        ]
        for plan in plans_data:
            obj, created = SubscriptionPlan.objects.get_or_create(
                name=plan["name"],
                defaults={"price": plan["price"], "duration_days": plan["duration_days"]},
            )
            status = "✅ created" if created else "⏭️  already exists"
            self.stdout.write(f"   {status}: {obj.get_name_display()} — {obj.price} грн")

        # ── 2. Courses ───────────────────────────────────────────────────────
        self.stdout.write("\n📚 Creating courses...")

        courses_data = [
            # ── PREMIUM ──────────────────────────────────────────────────────
            {
                "title": "Основи бюджетування",
                "description": (
                    "Опануйте мистецтво управління особистими фінансами: плануйте бюджет, "
                    "скорочуйте зайві витрати та формуйте подушку безпеки за перевіреними методами."
                ),
                "category": "budgeting",
                "price": "799.00",
                "is_premium": True,
                "is_active": True,
                "rating": "4.9",
            },
            {
                "title": "Фінансове планування сім'ї",
                "description": (
                    "Навчіться будувати спільний сімейний бюджет, розподіляти витрати між "
                    "членами родини та разом рухатись до великих фінансових цілей — першого "
                    "авто, квартири чи освіти дітей."
                ),
                "category": "general",
                "price": "1099.00",
                "is_premium": True,
                "is_active": True,
                "rating": "4.8",
            },
            {
                "title": "Фінансова грамотність для початківців",
                "description": (
                    "Стартовий курс для тих, хто хоче розібратись у фінансах з нуля: від "
                    "розуміння кредитів та депозитів до перших кроків в інвестиціях та "
                    "захисту від шахрайства."
                ),
                "category": "general",
                "price": "599.00",
                "is_premium": True,
                "is_active": True,
                "rating": "4.7",
            },
            # ── FREE ─────────────────────────────────────────────────────────
            {
                "title": "Фондовий ринок: що таке акції та як інвестувати",
                "description": (
                    "Дізнайтесь, як працює фондовий ринок, що таке акції та як звичайна "
                    "людина може почати інвестувати. Безкоштовний вступний урок для новачків."
                ),
                "category": "investing",
                "price": "0.00",
                "is_premium": False,
                "is_active": True,
                "rating": "4.6",
            },
            {
                "title": "Іпотека: як взяти кредит без помилок",
                "description": (
                    "Розберіться в умовах іпотечного кредитування, навчіться порівнювати "
                    "пропозиції банків та уникати прихованих комісій. Безкоштовний практичний урок."
                ),
                "category": "credit",
                "price": "0.00",
                "is_premium": False,
                "is_active": True,
                "rating": "4.7",
            },
            {
                "title": "Пенсійне планування: як забезпечити себе в майбутньому",
                "description": (
                    "Чи замислювались ви про пенсію у 30? Дізнайтесь про накопичувальні "
                    "системи, приватні пенсійні фонди та стратегії фінансової незалежності."
                ),
                "category": "pension",
                "price": "0.00",
                "is_premium": False,
                "is_active": True,
                "rating": "4.5",
            },
            {
                "title": "Інфляція: чому ваші гроші «худнуть» і що з цим робити",
                "description": (
                    "Зрозумійте, що таке інфляція, як вона впливає на ваші заощадження та "
                    "які інструменти допомагають зберегти купівельну спроможність грошей."
                ),
                "category": "general",
                "price": "0.00",
                "is_premium": False,
                "is_active": True,
                "rating": "4.5",
            },
            {
                "title": "Фінансові пастки: як захистити свої гроші від шахраїв",
                "description": (
                    "Навчіться розпізнавати фінансові піраміди, фішинг та маніпуляції "
                    "шахраїв. Реальні кейси та практичні поради, які збережуть ваші кошти."
                ),
                "category": "general",
                "price": "0.00",
                "is_premium": False,
                "is_active": True,
                "rating": "4.9",
            },
        ]

        created_courses = {}
        for data in courses_data:
            obj, created = Course.objects.get_or_create(
                title=data["title"],
                defaults={k: v for k, v in data.items() if k != "title"},
            )
            status = "✅ created" if created else "⏭️  already exists"
            premium_tag = "⭐ ПРЕМІУМ" if obj.is_premium else "🆓 FREE"
            self.stdout.write(f"   {status} [{premium_tag}]: {obj.title}")
            created_courses[obj.title] = obj

        # ── 3. Reviews ───────────────────────────────────────────────────────
        self.stdout.write("\n💬 Creating reviews...")

        # Find a reviewer — prefer superuser, else any user, else skip
        reviewer = User.objects.filter(is_superuser=True).first()
        if not reviewer:
            reviewer = User.objects.first()

        if not reviewer:
            self.stdout.write(
                self.style.WARNING(
                    "   ⚠️  No users found. Skipping reviews.\n"
                    "   Create a user first, then run: python manage.py populate_db"
                )
            )
        else:
            self.stdout.write(f"   Using user '{reviewer.username}' as reviewer.")

            reviews_data = [
                # ── Основи бюджетування ──
                {
                    "course_title": "Основи бюджетування",
                    "text": (
                        "Після цього курсу я вперше за 5 років почала відкладати гроші щомісяця. "
                        "Правило 50/30/20 змінило моє ставлення до витрат назавжди. "
                        "Рекомендую всім, хто хоче нарешті взяти фінанси під контроль!"
                    ),
                    "rating": 5,
                },
                {
                    "course_title": "Основи бюджетування",
                    "text": (
                        "Дуже структурований курс. Урок про відстеження витрат відкрив мені очі — "
                        "виявляється, я витрачав понад 3000 грн на місяць на речі, які мені не потрібні. "
                        "Дякую FinSmart!"
                    ),
                    "rating": 5,
                },
                # ── Фінансове планування сім'ї ──
                {
                    "course_title": "Фінансове планування сім'ї",
                    "text": (
                        "Ми з чоловіком постійно сварились через гроші. Після першого ж уроку "
                        "зрозуміли, що нам бракувало простої системи. Тепер ведемо спільний бюджет "
                        "вже 4 місяці — і жодного конфлікту через витрати!"
                    ),
                    "rating": 5,
                },
                {
                    "course_title": "Фінансове планування сім'ї",
                    "text": (
                        "Урок про спільні фінансові цілі — просто бомба. Ми поставили мету на "
                        "квартиру і вже знаємо, скільки відкладати щомісяця. Курс вартий кожної гривні."
                    ),
                    "rating": 5,
                },
                # ── Фінансова грамотність ──
                {
                    "course_title": "Фінансова грамотність для початківців",
                    "text": (
                        "Я завжди боялась фінансових тем, бо вони здавались надто складними. "
                        "Цей курс розкладає все по поличках — простою мовою, без жаргону. "
                        "Тепер я впевнено спілкуюсь з банківськими менеджерами!"
                    ),
                    "rating": 5,
                },
                {
                    "course_title": "Фінансова грамотність для початківців",
                    "text": (
                        "Урок про шахрайство варто показувати всім батькам і бабусям. "
                        "Дуже практичний матеріал. А блок про інвестиції мотивував мене "
                        "відкрити свій перший депозит. Дякую!"
                    ),
                    "rating": 4,
                },
                # ── Фондовий ринок ──
                {
                    "course_title": "Фондовий ринок: що таке акції та як інвестувати",
                    "text": (
                        "Нарешті зрозумів, що таке P/E ratio і навіщо диверсифікація. "
                        "Відмінний безкоштовний старт для тих, хто хоче почати інвестувати."
                    ),
                    "rating": 5,
                },
                {
                    "course_title": "Фондовий ринок: що таке акції та як інвестувати",
                    "text": (
                        "Доступно пояснені основи фондового ринку. Приємно, що є практичні "
                        "приклади з українськими реаліями. Коротко, але по суті."
                    ),
                    "rating": 4,
                },
                # ── Іпотека ──
                {
                    "course_title": "Іпотека: як взяти кредит без помилок",
                    "text": (
                        "Перед тим як іти до банку, прочитав цей урок — і встиг уникнути "
                        "кількох пасток з прихованими комісіями. Дуже практичний матеріал!"
                    ),
                    "rating": 5,
                },
                {
                    "course_title": "Іпотека: як взяти кредит без помилок",
                    "text": (
                        "Урок пояснює складні речі простою мовою. Тепер знаю різницю між "
                        "фіксованою та плаваючою ставкою. Дякую FinSmart за безкоштовний доступ!"
                    ),
                    "rating": 5,
                },
                # ── Пенсійне планування ──
                {
                    "course_title": "Пенсійне планування: як забезпечити себе в майбутньому",
                    "text": (
                        "Мені 28 і я ніколи не думав про пенсію. Після цього уроку відразу "
                        "відкрив накопичувальний рахунок. Краще пізно, ніж ніколи... а ще краще — рано!"
                    ),
                    "rating": 5,
                },
                {
                    "course_title": "Пенсійне планування: як забезпечити себе в майбутньому",
                    "text": (
                        "Пояснили різницю між солідарною та накопичувальною системою. "
                        "Нарешті зрозуміла, чому не варто розраховувати лише на державну пенсію."
                    ),
                    "rating": 4,
                },
                # ── Інфляція ──
                {
                    "course_title": "Інфляція: чому ваші гроші «худнуть» і що з цим робити",
                    "text": (
                        "Урок пояснив мені, чому тримати всі гроші на картці — погана ідея. "
                        "Тепер частину відкладаю в облігації. Просто та зрозуміло!"
                    ),
                    "rating": 5,
                },
                {
                    "course_title": "Інфляція: чому ваші гроші «худнуть» і що з цим робити",
                    "text": (
                        "Я думала, що інфляція — це щось абстрактне. Після цього уроку "
                        "зрозуміла, що це торкається кожного з нас щодня. Дуже наочно!"
                    ),
                    "rating": 4,
                },
                # ── Фінансові пастки ──
                {
                    "course_title": "Фінансові пастки: як захистити свої гроші від шахраїв",
                    "text": (
                        "Батьки ледь не потрапили в піраміду. Після того як я показав їм цей урок — "
                        "зупинились вчасно. Такий контент треба поширювати якомога ширше. Дякую!"
                    ),
                    "rating": 5,
                },
                {
                    "course_title": "Фінансові пастки: як захистити свої гроші від шахраїв",
                    "text": (
                        "Розбір реальних схем шахраїв — це те, що потрібно кожному. "
                        "Тепер знаю, на що звертати увагу при «інвестиційних пропозиціях». "
                        "Обов'язковий урок!"
                    ),
                    "rating": 5,
                },
            ]

            # Review model has unique_together = (user, course)
            # So we can only create ONE review per user per course.
            # We use the reviewer for all odd-indexed reviews,
            # and try a second user (or skip) for even-indexed ones.
            second_reviewer = User.objects.exclude(pk=reviewer.pk).first()

            for i, rdata in enumerate(reviews_data):
                course = created_courses.get(rdata["course_title"])
                if not course:
                    self.stdout.write(
                        self.style.WARNING(f"   ⚠️  Course not found: {rdata['course_title']}")
                    )
                    continue

                # Alternate reviewers to avoid the unique_together constraint
                current_reviewer = reviewer if i % 2 == 0 else second_reviewer
                if not current_reviewer:
                    self.stdout.write(
                        self.style.WARNING(
                            f"   ⚠️  Only 1 user exists — skipping 2nd review for '{rdata['course_title']}'"
                        )
                    )
                    continue

                obj, created = Review.objects.get_or_create(
                    user=current_reviewer,
                    course=course,
                    defaults={
                        "text": rdata["text"],
                        "rating": rdata["rating"],
                        "is_approved": True,
                    },
                )
                status = "✅ created" if created else "⏭️  already exists"
                self.stdout.write(
                    f"   {status}: [{current_reviewer.username}] → {course.title[:40]}..."
                )

        # ── Done ─────────────────────────────────────────────────────────────
        self.stdout.write("\n" + "─" * 55)
        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully!"))
        self.stdout.write(f"   Courses:  {Course.objects.count()}")
        self.stdout.write(f"   Plans:    {SubscriptionPlan.objects.count()}")
        self.stdout.write(f"   Reviews:  {Review.objects.count()} (approved: {Review.objects.filter(is_approved=True).count()})")
        self.stdout.write("─" * 55 + "\n")
