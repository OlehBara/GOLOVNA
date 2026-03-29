import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finsmart_project.settings")
django.setup()

from main.models import Course

free_courses_data = [
    {
        "title": "Фондовий ринок для початківців",
        "description": "Базові знання про фондовий ринок: акції, облігації, ETF. Як почати інвестувати з мінімальними ризиками.",
        "category": "investing",
        "price": 0.00,
        "is_premium": False,
        "is_active": True,
        "rating": 5.0,
    },
    {
        "title": "Іпотека та житлові кредити",
        "description": "Все, що потрібно знати перед тим, як брати іпотеку. Як розрахувати переплату та вибрати найкращі умови.",
        "category": "credit",
        "price": 0.00,
        "is_premium": False,
        "is_active": True,
        "rating": 5.0,
    },
    {
        "title": "Пенсійне планування",
        "description": "Як забезпечити собі гідну старість? Розбираємо державні та недержавні пенсійні фонди, складний відсоток.",
        "category": "pension",
        "price": 0.00,
        "is_premium": False,
        "is_active": True,
        "rating": 5.0,
    },
    {
        "title": "Фінансові пастки та шахрайство",
        "description": "Як розпізнати фінансову піраміду, скам-проекти та захистити свої гроші від шахраїв в інтернеті.",
        "category": "general",
        "price": 0.00,
        "is_premium": False,
        "is_active": True,
        "rating": 5.0,
    },
    {
        "title": "Інфляція: чому ціни ростуть",
        "description": "Що таке інфляція, як вона впливає на ваші заощадження та як захистити свої гроші від знецінення.",
        "category": "general",
        "price": 0.00,
        "is_premium": False,
        "is_active": True,
        "rating": 5.0,
    },
]

created_count = 0
for course_data in free_courses_data:
    course, created = Course.objects.get_or_create(
        title=course_data["title"], defaults=course_data
    )
    if created:
        created_count += 1
        print(f"Created: {course.title}")
    else:
        print(f"Already exists: {course.title}")

print(f"Successfully added {created_count} new free courses.")
