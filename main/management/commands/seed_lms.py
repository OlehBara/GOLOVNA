from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from main.models import Course, Enrollment, Lesson, Quiz


class Command(BaseCommand):
    help = "Створює демо-LMS контент: 3 преміум-курси, уроки, відео та тести, а також записує всіх користувачів на ці курси."

    def handle(self, *args, **options):
        User = get_user_model()

        courses_data = [
            {
                "title": "FinSmart: Бюджет та заощадження",
                "description": "Покрокова система управління особистим бюджетом, подушка безпеки та цілі за методом SMART.",
                "category": "budgeting",
                "price": 39.00,
                "is_premium": True,
                "lessons": [
                    # Модуль 1
                    {
                        "title": "Чому бюджет — це не обмеження, а свобода",
                        "order": 1,
                        "video_url": "https://www.youtube.com/embed/DW0YIu9Kv0Q",
                        "duration": "~10 хв",
                        "content": "У цьому уроці розберемо, чому бюджет — це інструмент свободи, а не заборон...",
                        "quiz": {
                            "question": "Яка головна мета особистого бюджету?",
                            "a": "Обмежити всі витрати до мінімуму",
                            "b": "Дати контроль над грошима та впевненість у майбутньому",
                            "c": "Вести записи лише для статистики",
                            "correct": "b",
                        },
                    },
                    {
                        "title": "Правило 50/30/20 на практиці",
                        "order": 2,
                        "video_url": "https://www.youtube.com/embed/6V8K9Fq8f5w",
                        "duration": "~12 хв",
                        "content": "Розбираємо правило 50/30/20 та адаптацію під українські реалії...",
                        "quiz": {
                            "question": "Що означають 20% у правилі 50/30/20?",
                            "a": "Розваги",
                            "b": "Обов'язкові платежі",
                            "c": "Заощадження та інвестиції",
                            "correct": "c",
                        },
                    },
                    {
                        "title": "Як відстежувати витрати без болю",
                        "order": 3,
                        "video_url": "https://www.youtube.com/embed/VY4P2pCjC4k",
                        "duration": "~9 хв",
                        "content": "Огляд простих інструментів: таблиця, мобільний додаток, конверти...",
                        "quiz": {
                            "question": "Який підхід допомагає найкраще побачити «дірки» у витратах?",
                            "a": "Не відстежувати дрібні суми",
                            "b": "Записувати всі витрати хоча б 30 днів",
                            "c": "Раз на рік аналізувати виписку по картці",
                            "correct": "b",
                        },
                    },
                    # Модуль 2
                    {
                        "title": "Створення подушки безпеки",
                        "order": 4,
                        "video_url": "https://www.youtube.com/embed/2uYgP0x2tjQ",
                        "duration": "~11 хв",
                        "content": "Що таке фінансова подушка, де її зберігати та як її формувати поетапно...",
                        "quiz": {
                            "question": "Який рекомендований розмір подушки безпеки?",
                            "a": "1 місяць витрат",
                            "b": "3–6 місяців обов'язкових витрат",
                            "c": "12 місяців доходу",
                            "correct": "b",
                        },
                    },
                    {
                        "title": "Типові помилки при заощадженні",
                        "order": 5,
                        "video_url": "https://www.youtube.com/embed/QeTt7PLkZXM",
                        "duration": "~8 хв",
                        "content": "Розбираємо найчастіші помилки: заощаджувати «з того, що залишиться»...",
                        "quiz": {
                            "question": "Що знижує шанси успішного заощадження?",
                            "a": "Автоматичне відкладення коштів одразу після отримання доходу",
                            "b": "Чекати кінця місяця і відкладати «якщо щось лишиться»",
                            "c": "Планувати суму заощаджень заздалегідь",
                            "correct": "b",
                        },
                    },
                ],
            },
            {
                "title": "FinSmart: Інвестиції для початківців",
                "description": "Базовий курс про акції, облігації, ETF та формування довгострокового портфеля.",
                "category": "investing",
                "price": 59.00,
                "is_premium": True,
                "lessons": [
                    # Модуль 1
                    {
                        "title": "Що таке інвестиції та чим вони відрізняються від спекуляцій",
                        "order": 1,
                        "video_url": "https://www.youtube.com/embed/vwE8oLQY6h8",
                        "duration": "~12 хв",
                        "content": "Розбираємо базові терміни: актив, пасив, дохідність, ризик...",
                        "quiz": {
                            "question": "Головна мета довгострокового інвестора — це:",
                            "a": "Швидко подвоїти капітал за кілька днів",
                            "b": "Системно нарощувати капітал протягом років",
                            "c": "Постійно купувати та продавати щодня",
                            "correct": "b",
                        },
                    },
                    {
                        "title": "Акції, облігації та індексні фонди",
                        "order": 2,
                        "video_url": "https://www.youtube.com/embed/kl0i0mLwM1U",
                        "duration": "~14 хв",
                        "content": "Порівнюємо інструменти: ризики, дохідність, роль у портфелі...",
                        "quiz": {
                            "question": "Що таке ETF?",
                            "a": "Окрема акція компанії",
                            "b": "Фонд, який слідкує за індексом чи кошиком активів",
                            "c": "Вид банківського депозиту",
                            "correct": "b",
                        },
                    },
                    # Модуль 2
                    {
                        "title": "Диверсифікація та управління ризиком",
                        "order": 3,
                        "video_url": "https://www.youtube.com/embed/0JXbI7bY9_c",
                        "duration": "~10 хв",
                        "content": "Чому не можна вкладати все в одну акцію і як збалансувати портфель...",
                        "quiz": {
                            "question": "Чому диверсифікація важлива?",
                            "a": "Зменшує залежність портфеля від одного активу",
                            "b": "Гарантує 100% дохідність",
                            "c": "Лише збільшує кількість комісій",
                            "correct": "a",
                        },
                    },
                    {
                        "title": "Горизонт інвестування та стратегія DCA",
                        "order": 4,
                        "video_url": "https://www.youtube.com/embed/UPBblBHNnyk",
                        "duration": "~11 хв",
                        "content": "Стратегія регулярного інвестування (Dollar-Cost Averaging) для новачків...",
                        "quiz": {
                            "question": "У чому суть стратегії DCA?",
                            "a": "Інвестувати випадкові суми у випадкові дні",
                            "b": "Регулярно інвестувати фіксовану суму незалежно від ціни",
                            "c": "Чекати і купувати лише коли ринок «на дні»",
                            "correct": "b",
                        },
                    },
                ],
            },
            {
                "title": "FinSmart: Кредит, борги та фінансова безпека",
                "description": "Як безпечно користуватись кредитами, виходити з боргів та захищати себе від фінансових ризиків.",
                "category": "credit",
                "price": 49.00,
                "is_premium": True,
                "lessons": [
                    {
                        "title": "Хороший і поганий борг",
                        "order": 1,
                        "video_url": "https://www.youtube.com/embed/Zv11L-ZfrS0",
                        "duration": "~9 хв",
                        "content": "Пояснюємо різницю між боргом, який допомагає зростати, та боргом, який тягне вниз...",
                        "quiz": {
                            "question": "Що можна вважати «поганим боргом»?",
                            "a": "Кредит на розвиток бізнесу з продуманим планом",
                            "b": "Кредит на споживчі покупки без плану погашення",
                            "c": "Довгострокову іпотеку з фіксованою ставкою",
                            "correct": "b",
                        },
                    },
                    {
                        "title": "Кредитні картки без пасток",
                        "order": 2,
                        "video_url": "https://www.youtube.com/embed/I4qzr0Xl2uQ",
                        "duration": "~10 хв",
                        "content": "Пільговий період, мінімальний платіж, пеня — що це і як не потрапити в боргову спіраль...",
                        "quiz": {
                            "question": "Як безпечніше користуватися кредитною карткою?",
                            "a": "Платити лише мінімальний платіж",
                            "b": "Закривати повну заборгованість у пільговий період",
                            "c": "Використовувати весь доступний кредитний ліміт",
                            "correct": "b",
                        },
                    },
                    {
                        "title": "План виходу з боргів",
                        "order": 3,
                        "video_url": "https://www.youtube.com/embed/_a17cG95-Wc",
                        "duration": "~12 хв",
                        "content": "Стратегії «снігова куля» та «лавина» для погашення кількох кредитів...",
                        "quiz": {
                            "question": "У чому суть стратегії «лавина»?",
                            "a": "Спочатку гасимо найменший за сумою борг",
                            "b": "Спочатку гасимо борг із найвищою відсотковою ставкою",
                            "c": "Платимо рівномірно за всіма боргами",
                            "correct": "b",
                        },
                    },
                ],
            },
        ]

        self.stdout.write(
            self.style.MIGRATE_HEADING("Створення курсів, уроків та тестів...")
        )

        for course_info in courses_data:
            course, created = Course.objects.get_or_create(
                title=course_info["title"],
                defaults={
                    "description": course_info["description"],
                    "category": course_info["category"],
                    "price": course_info["price"],
                    "is_premium": course_info["is_premium"],
                    "is_active": True,
                },
            )

            if not created:
                # Оновлюємо основні поля, якщо курс вже існує
                course.description = course_info["description"]
                course.category = course_info["category"]
                course.price = course_info["price"]
                course.is_premium = course_info["is_premium"]
                course.is_active = True
                course.save()

            self.stdout.write(
                f"- Курс: {course.title} ({'створено' if created else 'оновлено'})"
            )

            # Створюємо уроки та тести
            for lesson_data in course_info["lessons"]:
                lesson, _ = Lesson.objects.get_or_create(
                    course=course,
                    order=lesson_data["order"],
                    defaults={
                        "title": lesson_data["title"],
                        "video_url": lesson_data["video_url"],
                        "content": lesson_data["content"],
                        "duration": lesson_data["duration"],
                    },
                )
                # Якщо урок вже існує – оновлюємо текст/відео
                lesson.title = lesson_data["title"]
                lesson.video_url = lesson_data["video_url"]
                lesson.content = lesson_data["content"]
                lesson.duration = lesson_data["duration"]
                lesson.save()

                quiz_data = lesson_data["quiz"]
                quiz, _ = Quiz.objects.get_or_create(
                    lesson=lesson,
                    defaults={
                        "question": quiz_data["question"],
                        "option_a": quiz_data["a"],
                        "option_b": quiz_data["b"],
                        "option_c": quiz_data["c"],
                        "correct_answer": quiz_data["correct"],
                    },
                )
                quiz.question = quiz_data["question"]
                quiz.option_a = quiz_data["a"]
                quiz.option_b = quiz_data["b"]
                quiz.option_c = quiz_data["c"]
                quiz.correct_answer = quiz_data["correct"]
                quiz.save()

        # Автоматично записуємо всіх користувачів на всі 3 курси,
        # щоб одразу був доступ до уроків
        self.stdout.write(
            self.style.MIGRATE_HEADING("Реєстрація користувачів на курси...")
        )
        all_courses = Course.objects.filter(is_premium=True, is_active=True)
        for user in User.objects.all():
            for course in all_courses:
                Enrollment.objects.get_or_create(user=user, course=course)

        self.stdout.write(
            self.style.SUCCESS(
                "LMS-контент успішно створено. "
                "Запусти сервер і заходь у профіль, щоб проходити уроки."
            )
        )
