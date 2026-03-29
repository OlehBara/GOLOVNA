import json
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse, Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# from django.contrib.auth.forms import UserCreationForm # Replaced by custom form
from .forms import ProfileUpdateForm, UserRegistrationForm, UserUpdateForm
from .models import (
    CartItem, ContactMessage, Course, Enrollment,
    LessonProgress, Review, StudentVerification, SubscriptionPlan,
    UserSubscription,
)


def _get_active_owned_subscription(user):
    if not user.is_authenticated:
        return None
    try:
        sub = user.subscription_owner
    except ObjectDoesNotExist:
        return None

    if sub.is_active and sub.end_date > timezone.now():
        return sub
    return None


def has_student_discount(user):
    sub = _get_active_owned_subscription(user)
    return bool(sub and sub.plan and sub.plan.name == "student")


def _get_active_family_subscription(user):
    sub = _get_active_owned_subscription(user)
    if sub and sub.plan and sub.plan.name == "family":
        return sub
    return None


def get_course_price_for_user(user, course):
    base_price = course.price or Decimal("0.00")
    if has_student_discount(user):
        return (base_price * Decimal("0.5")).quantize(Decimal("0.01"))
    return base_price


def _resolve_course_conspect_path(course_id: int):
    """PDF у static/conspects/course_<id>.pdf або default.pdf."""
    base = Path(settings.BASE_DIR) / "static" / "conspects"
    specific = base / f"course_{course_id}.pdf"
    if specific.is_file():
        return specific
    default = base / "default.pdf"
    if default.is_file():
        return default
    return None


def register(request):
    """Реєстрація нового користувача"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Реєстрація успішна! Ласкаво просимо.")
            return redirect("index")
        else:
            messages.error(request, "Помилка реєстрації. Перевірте введені дані.")
    else:
        form = UserRegistrationForm()

    return render(request, "main/register.html", {"form": form})


@login_required
def profile_view(request):
    """Особистий кабінет користувача"""
    user_courses = Enrollment.objects.filter(
        user=request.user, is_completed=False, course__is_premium=True
    ).select_related("course")

    completed_courses = Enrollment.objects.filter(
        user=request.user, is_completed=True
    ).select_related("course")

    try:
        owned_subscription = request.user.subscription_owner
    except ObjectDoesNotExist:
        owned_subscription = None

    shared_subscription = (
        request.user.shared_subscriptions.filter(
            is_active=True,
            end_date__gt=timezone.now(),
            plan__name="family",
        )
        .select_related("owner", "plan")
        .first()
    )

    has_subscription_access = bool(
        _get_active_owned_subscription(request.user) or shared_subscription
    )
    enrolled_course_ids = set(
        Enrollment.objects.filter(user=request.user).values_list("course_id", flat=True)
    )
    subscription_courses = Course.objects.filter(
        is_active=True,
        is_premium=True,
    ).exclude(id__in=enrolled_course_ids) if has_subscription_access else Course.objects.none()

    context = {
        "display_name": request.user.username,
        "display_email": request.user.email,
        "user_courses": user_courses,
        "completed_courses": completed_courses,
        "subscription": owned_subscription,
        "owned_subscription": owned_subscription,
        "shared_subscription": shared_subscription,
        "subscription_courses": subscription_courses,
    }
    context["my_subscriptions"] = UserSubscription.objects.filter(
        owner=request.user, is_active=True, end_date__gt=timezone.now()
    ).select_related("plan")
    return render(request, "main/profile.html", context)


@login_required
def edit_profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Ваш акаунт оновлено!")
            return redirect("profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"u_form": u_form, "p_form": p_form}

    return render(request, "main/edit_profile.html", context)


def index(request):
    """Головна сторінка"""
    free_courses = Course.objects.filter(is_active=True, is_premium=False, price=0)

    premium_courses = Course.objects.filter(is_active=True, is_premium=True)[:3]
    for course in premium_courses:
        course.display_price = get_course_price_for_user(request.user, course)
        course.has_student_discount = has_student_discount(request.user)

    testimonials = Review.objects.filter(is_approved=True).select_related("user")[:4]

    # Subscription data
    subscription_plans = SubscriptionPlan.objects.all()
    student_verification_status = None
    if request.user.is_authenticated:
        sv = StudentVerification.objects.filter(user=request.user).order_by("-submitted_at").first()
        if sv:
            student_verification_status = sv.status

    context = {
        "popular_courses": free_courses,
        "premium_courses": premium_courses,
        "testimonials": testimonials,
        "subscription_plans": subscription_plans,
        "student_verification_status": student_verification_status,
    }
    return render(request, "main/index.html", context)


def courses(request):
    """Сторінка курсів"""
    # Отримуємо курси за категоріями (строга фільтрація)
    premium_courses = Course.objects.filter(is_active=True, is_premium=True)

    # "Звичайні" курси (безкоштовні та платні не-преміум) для загального каталогу
    # Використовуємо is_premium=False, щоб преміум курси не потрапляли сюди
    courses_list = Course.objects.filter(is_active=True, is_premium=False)

    # Фільтрація за категорією
    category = request.GET.get("category", "all")
    if category != "all":
        courses_list = courses_list.filter(category=category)

    # Пошук
    search = request.GET.get("search", "")
    if search:
        courses_list = courses_list.filter(
            models.Q(title__icontains=search) | models.Q(description__icontains=search)
        )

    # IDs курсів що вже придбані — для показу правильного стану кнопок
    enrolled_ids = set()
    if request.user.is_authenticated:
        enrolled_ids = set(
            Enrollment.objects.filter(user=request.user).values_list(
                "course_id", flat=True
            )
        )

    context = {
        "courses": courses_list,
        "premium_courses": premium_courses,
        "current_category": category,
        "search_query": search,
        "enrolled_ids": enrolled_ids,
    }
    discount_enabled = has_student_discount(request.user)
    for course in premium_courses:
        course.display_price = get_course_price_for_user(request.user, course)
        course.has_student_discount = discount_enabled

    for course in courses_list:
        course.display_price = get_course_price_for_user(request.user, course)
        course.has_student_discount = discount_enabled

    return render(request, "main/courses.html", context)


def course_detail(request, course_id):
    """Сторінка детального опису курсу"""
    course = get_object_or_404(Course, id=course_id)

    # Рекомендації: інші курси з тієї ж категорії
    related_courses = Course.objects.filter(
        category=course.category, is_active=True
    ).exclude(id=course.id)[:3]

    # Перевірка: чи вже придбав користувач цей курс
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = has_course_access(request.user, course)

    # Перевірка: чи курс вже є в кошику
    in_cart = False
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(user=request.user, course=course).exists()
    else:
        session_key = request.session.session_key
        if session_key:
            in_cart = CartItem.objects.filter(
                session_key=session_key, course=course
            ).exists()

    # Static modules list (can be replaced by a DB model later)
    modules = [
        {
            "title": "Модуль 1: Основи фінансової грамотності",
            "lessons": [
                "Що таке особистий бюджет?",
                "Правило 50/30/20",
                "Психологія грошей",
            ],
            "duration": "2 год 15 хв",
        },
        {
            "title": "Модуль 2: Інструменти управління грошима",
            "lessons": [
                "Банківські вклади та депозити",
                "Картки та cashback-стратегії",
                "Мобільні застосунки для бюджету",
            ],
            "duration": "1 год 50 хв",
        },
        {
            "title": "Модуль 3: Інвестиції для початківців",
            "lessons": [
                "Фондовий ринок: базові поняття",
                "ETF та диверсифікація",
                "Ризики та їх мінімізація",
            ],
            "duration": "3 год 10 хв",
        },
        {
            "title": "Модуль 4: Довгострокова стратегія",
            "lessons": [
                "Пенсійне планування",
                "Страхування та захист активів",
                "Ваш фінансовий план на 10 років",
            ],
            "duration": "2 год 30 хв",
        },
    ]

    context = {
        "course": course,
        "display_price": get_course_price_for_user(request.user, course),
        "has_student_discount": has_student_discount(request.user),
        "related_courses": related_courses,
        "is_enrolled": is_enrolled,
        "in_cart": in_cart,
        "is_purchased": is_enrolled,  # semantic alias used in template
        "has_conspect": _resolve_course_conspect_path(course.id) is not None,
        "modules": modules,
        "course_reviews": Review.objects.filter(course=course, is_approved=True)
        .select_related("user")
        .order_by("-created_at"),
    }
    return render(request, "main/course_detail.html", context)


@login_required
def course_conspect_download(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not has_course_access(request.user, course):
        return HttpResponseForbidden("Немає доступу до цього курсу.")

    path = _resolve_course_conspect_path(course_id)
    if not path:
        raise Http404("Файл конспекту не знайдено.")

    safe = slugify(course.title)[:80] or f"course_{course_id}"
    filename = f"konspet_{safe}.pdf"
    return FileResponse(
        path.open("rb"),
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )


def about(request):
    """Сторінка 'Про нас'"""
    stats = {
        "total_courses": Course.objects.filter(is_active=True).count(),
        "total_reviews": Review.objects.filter(is_approved=True).count(),
        "satisfaction_rate": 98,
    }

    context = {"stats": stats}

    # Секретна інбокс-секція лише для адміна 'mysite'
    if request.user.is_authenticated and request.user.username == "mysite":
        context["admin_messages"] = ContactMessage.objects.all().order_by("-created_at")

    return render(request, "main/about.html", context)


def contact(request):
    """Сторінка контактів"""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            # Зберігаємо повідомлення в базу
            ContactMessage.objects.create(name=name, email=email, message=message)
            messages.success(request, "Дякуємо, ваше повідомлення відправлено!")
            return redirect("contact")
        else:
            messages.error(request, "Будь ласка, заповніть всі поля.")

    return render(request, "main/contact.html")


@csrf_exempt
@require_http_methods(["POST"])
def contact_ajax(request):
    """AJAX обробка контактної форми"""
    try:
        # Try JSON first (fetch with Content-Type: application/json)
        content_type = request.content_type or ""
        if "application/json" in content_type:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            subject = data.get("subject", "").strip()
            message = data.get("message", "").strip()
        else:
            # Fallback: FormData / urlencoded
            name = request.POST.get("name", "").strip()
            email = request.POST.get("email", "").strip()
            subject = request.POST.get("subject", "").strip()
            message = request.POST.get("message", "").strip()

        print(
            f"[contact_ajax] ct={content_type!r} name={name!r} email={email!r} msg={message!r}"
        )

        if name and email and message:
            ContactMessage.objects.create(
                sender=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
            return JsonResponse(
                {"success": True, "message": "Дякуємо, ваше повідомлення відправлено!"}
            )
        else:
            return JsonResponse(
                {"success": False, "message": "Будь ласка, заповніть усі поля."}
            )

    except Exception as e:
        import traceback

        print("contact_ajax error:", traceback.format_exc())
        return JsonResponse({"success": False, "message": f"Помилка: {str(e)}"})


@login_required
@require_http_methods(["POST"])
def enroll_course(request, course_id):
    """AJAX: записати користувача на курс (постійний стан)"""
    try:
        course = get_object_or_404(Course, id=course_id)
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user, course=course
        )
        return JsonResponse(
            {
                "success": True,
                "already_enrolled": not created,
                "message": f'Ви успішно придбали курс "{course.title}"!',
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def mark_premium_lesson_complete(request):
    """AJAX: позначити урок преміум-курсу як завершений"""
    try:
        content_type = request.content_type or ""
        if "application/json" in content_type:
            data = json.loads(request.body)
        else:
            data = request.POST

        course_id = data.get("course_id")
        lesson_key = (data.get("lesson_key") or "").strip()
        is_final = data.get("is_final", False)

        if isinstance(is_final, str):
            is_final = is_final.lower() in ("1", "true", "yes")

        if not course_id or not lesson_key:
            return JsonResponse(
                {"success": False, "message": "Missing course_id or lesson_key"},
                status=400,
            )

        course = get_object_or_404(Course, id=course_id)

        if not has_course_access(request.user, course):
            return JsonResponse(
                {"success": False, "message": "Not enrolled"}, status=403
            )

        progress, _ = LessonProgress.objects.get_or_create(
            user=request.user, course=course, lesson_key=lesson_key
        )
        progress.status = "completed"
        progress.completed_at = timezone.now()
        progress.save()

        if is_final:
            Enrollment.objects.filter(user=request.user, course=course).update(
                is_completed=True, completion_date=timezone.now()
            )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def submit_review(request):
    """AJAX: створити/оновити відгук за курсом"""
    try:
        content_type = request.content_type or ""
        if "application/json" in content_type:
            data = json.loads(request.body)
        else:
            data = request.POST

        course_id = data.get("course_id")
        text = (data.get("text") or "").strip()
        rating_raw = data.get("rating")

        try:
            rating = int(rating_raw)
        except (TypeError, ValueError):
            rating = 0

        if not course_id or not text or not (1 <= rating <= 5):
            return JsonResponse(
                {"success": False, "message": "Invalid data"}, status=400
            )

        course = get_object_or_404(Course, id=course_id)

        if not has_course_access(request.user, course):
            return JsonResponse(
                {"success": False, "message": "Not enrolled"}, status=403
            )

        Review.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={
                "text": text,
                "rating": rating,
                "is_approved": False,
            },
        )

        return JsonResponse(
            {"success": True, "message": "Дякуємо! Відгук надіслано на модерацію."}
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def add_to_cart(request, course_id):
    """Додавання курсу в кошик (AJAX)"""
    try:
        course = Course.objects.get(id=course_id)

        # ── Guard: користувач вже має доступ — не додаємо в кошик ──
        if request.user.is_authenticated:
            if has_course_access(request.user, course):
                return JsonResponse(
                    {
                        "success": False,
                        "already_enrolled": True,
                        "message": f'У вас вже є доступ до курсу "{course.title}"',
                    }
                )

        if request.user.is_authenticated:
            # Для авторизованих користувачів
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user, course=course
            )
            count = CartItem.objects.filter(user=request.user).count()
        else:
            # Для анонімних користувачів (по сесії)
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            cart_item, created = CartItem.objects.get_or_create(
                session_key=session_key, course=course
            )
            count = CartItem.objects.filter(session_key=session_key).count()

        return JsonResponse(
            {
                "success": True,
                "message": f'Курс "{course.title}" додано до кошика',
                "cart_count": count,
            }
        )

    except Course.DoesNotExist:
        return JsonResponse({"success": False, "message": "Курс не знайдено"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


def cart_detail(request):
    """Сторінка кошика"""
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user).select_related("course", "plan")
    else:
        session_key = request.session.session_key
        if not session_key:
            cart_items = []
        else:
            cart_items = CartItem.objects.filter(
                session_key=session_key
            ).select_related("course", "plan")

    total_price = Decimal("0.00")
    for item in cart_items:
        if item.course:
            item.display_price = get_course_price_for_user(request.user, item.course)
            total_price += item.display_price
        elif item.plan:
            item.display_price = item.plan.price
            total_price += item.plan.price

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, "main/cart.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    """Видалення курсу з кошика (AJAX)"""
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(id=item_id, user=request.user).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                return JsonResponse({"success": False, "message": "Session not found"})
            cart_item = CartItem.objects.filter(
                id=item_id, session_key=session_key
            ).first()

        if cart_item:
            cart_item.delete()

            # Recalculate totals
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                cart_items = CartItem.objects.filter(
                    session_key=request.session.session_key
                )

            count = cart_items.count()
            total_price = Decimal("0.00")
            for item in cart_items:
                if item.course:
                    total_price += get_course_price_for_user(request.user, item.course)
                elif item.plan:
                    total_price += item.plan.price or Decimal("0.00")

            return JsonResponse(
                {
                    "success": True,
                    "message": "Курс видалено з кошика",
                    "cart_count": count,
                    "total_price": float(total_price),
                }
            )
        else:
            return JsonResponse({"success": False, "message": "Товар не знайдено"})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


# ──────────────────────────────────────────────
#  ADMIN-ONLY VIEWS
# ──────────────────────────────────────────────
from django.contrib.admin.views.decorators import staff_member_required

from .forms import CourseForm


@staff_member_required
def add_course(request):
    """Адмін: додати новий курс"""
    form = CourseForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        course = form.save()
        messages.success(request, f'Курс "{course.title}" успішно додано!')
        return redirect("course_detail", course_id=course.id)
    return render(request, "main/add_course.html", {"form": form, "action": "Додати"})


@staff_member_required
def edit_course(request, course_id):
    """Адмін: редагувати курс"""
    course = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f'Курс "{course.title}" оновлено!')
        return redirect("course_detail", course_id=course.id)
    return render(
        request,
        "main/add_course.html",
        {"form": form, "course": course, "action": "Редагувати"},
    )


@staff_member_required
def delete_course(request, course_id):
    """Адмін: видалити курс"""
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        title = course.title
        course.delete()
        messages.success(request, f'Курс "{title}" видалено.')
        return redirect("courses")
    return render(request, "main/delete_course_confirm.html", {"course": course})


# ──────────────────────────────────────────────
#  PAYMENT (FAKE GATEWAY)
# ──────────────────────────────────────────────


@login_required
def checkout(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user).select_related("course", "plan")
    else:
        session_key = request.session.session_key
        cart_items = (
            CartItem.objects.filter(session_key=session_key).select_related("course", "plan")
            if session_key
            else []
        )

    if not cart_items:
        messages.info(request, "Ваш кошик порожній.")
        return redirect("cart_detail")

    total_price = Decimal("0.00")
    for item in cart_items:
        if item.course:
            item.display_price = get_course_price_for_user(request.user, item.course)
            total_price += item.display_price
        elif item.plan:
            item.display_price = item.plan.price
            total_price += item.plan.price

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, "main/payment.html", context)


@login_required
@require_http_methods(["POST"])
def process_payment(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related("course", "plan")

    enrolled_count = 0
    for item in cart_items:
        if item.course:
            Enrollment.objects.get_or_create(user=request.user, course=item.course)
            enrolled_count += 1
        elif item.plan:
            from datetime import timedelta
            end_date = timezone.now() + timedelta(days=item.plan.duration_days)
            UserSubscription.objects.update_or_create(
                owner=request.user,
                defaults={"plan": item.plan, "end_date": end_date, "is_active": True},
            )
            enrolled_count += 1

    cart_items.delete()

    if enrolled_count:
        messages.success(
            request,
            f"✅ Оплата успішна! Ви придбали {enrolled_count} позицій(ї).",
        )
    else:
        messages.info(request, "Кошик був порожній — нічого не оплачено.")

    return redirect("profile")


@login_required
def payment_success(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related("course", "plan")

    enrolled_count = 0
    for item in cart_items:
        if item.course:
            Enrollment.objects.get_or_create(user=request.user, course=item.course)
            enrolled_count += 1
        elif item.plan:
            from datetime import timedelta
            end_date = timezone.now() + timedelta(days=item.plan.duration_days)
            UserSubscription.objects.update_or_create(
                owner=request.user,
                defaults={"plan": item.plan, "end_date": end_date, "is_active": True},
            )
            enrolled_count += 1

    cart_items.delete()

    if enrolled_count:
        messages.success(
            request,
            f"🎉 Вітаємо! Ви успішно придбали {enrolled_count} позицій(ї). Приємного навчання!",
        )
    else:
        messages.info(request, "Кошик був порожній.")

    return redirect("profile")


# ─── Course 1: Основи бюджетування ───────────────────────────────────────────
def _get_premium_course_by_keyword(keyword):
    return Course.objects.filter(is_premium=True, title__icontains=keyword).first()


@login_required
def lesson_budgeting_1(request):
    return render(request, "main/lesson_budgeting_1.html")


@login_required
def lesson_budgeting_2(request):
    return render(request, "main/lesson_budgeting_2.html")


@login_required
def lesson_budgeting_3(request):
    return render(request, "main/lesson_budgeting_3.html")


@login_required
def lesson_budgeting_4(request):
    course = _get_premium_course_by_keyword("бюджет")
    existing_review = None
    if course:
        existing_review = Review.objects.filter(
            user=request.user, course=course
        ).first()
    return render(
        request,
        "main/lesson_budgeting_4.html",
        {
            "course": course,
            "existing_review": existing_review,
        },
    )


# ─── Course 2: Фінансове планування сім'ї ────────────────────────────────────
@login_required
def lesson_family_1(request):
    return render(request, "main/lesson_family_1.html")


@login_required
def lesson_family_2(request):
    return render(request, "main/lesson_family_2.html")


@login_required
def lesson_family_3(request):
    return render(request, "main/lesson_family_3.html")


@login_required
def lesson_family_4(request):
    course = _get_premium_course_by_keyword("сім")
    existing_review = None
    if course:
        existing_review = Review.objects.filter(
            user=request.user, course=course
        ).first()
    return render(
        request,
        "main/lesson_family_4.html",
        {
            "course": course,
            "existing_review": existing_review,
        },
    )


# ─── Course 3: Фінансова грамотність для початківців ─────────────────────────
@login_required
def lesson_literacy_1(request):
    return render(request, "main/lesson_literacy_1.html")


@login_required
def lesson_literacy_2(request):
    return render(request, "main/lesson_literacy_2.html")


@login_required
def lesson_literacy_3(request):
    return render(request, "main/lesson_literacy_3.html")


@login_required
def lesson_literacy_4(request):
    course = _get_premium_course_by_keyword("грамот")
    existing_review = None
    if course:
        existing_review = Review.objects.filter(
            user=request.user, course=course
        ).first()
    return render(
        request,
        "main/lesson_literacy_4.html",
        {
            "course": course,
            "existing_review": existing_review,
        },
    )


# ─── Free Courses ─────────────────────────────────────────────────────────────

# Маппінг: частина назви курсу → шаблон
FREE_COURSE_TEMPLATE_MAP = {
    "Фондовий ринок": "main/lesson_free_stock.html",
    "Іпотека": "main/lesson_free_mortgage.html",
    "Пенсійне": "main/lesson_free_pension.html",
    "Фінансові пастки": "main/lesson_free_scam.html",
    "Інфляція": "main/lesson_free_inflation.html",
}


@login_required
def free_lesson(request, course_id):
    """Сторінка безкоштовного уроку"""
    course = get_object_or_404(Course, id=course_id, is_premium=False)

    # Автоматично створюємо Enrollment якщо ще немає
    Enrollment.objects.get_or_create(user=request.user, course=course)

    template = None
    for key, tmpl in FREE_COURSE_TEMPLATE_MAP.items():
        if key in course.title:
            template = tmpl
            break

    if not template:
        template = "main/lesson_free.html"

    return render(request, template, {"course": course})


@login_required
@require_http_methods(["POST"])
def mark_lesson_complete(request):
    """AJAX: позначити безкоштовний курс як завершений"""
    try:
        data = json.loads(request.body)
        course_id = data.get("course_id")
        course = get_object_or_404(Course, id=course_id)
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user, course=course
        )
        enrollment.is_completed = True
        enrollment.completion_date = timezone.now()
        enrollment.save()

        return JsonResponse(
            {"success": True, "message": f'Курс "{course.title}" успішно завершено!'}
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


# ── Subscription System Views ─────────────────────────────────────

def has_course_access(user, course):
    """Перевіряє чи має користувач доступ до курсу."""
    if not user.is_authenticated:
        return False
    if Enrollment.objects.filter(user=user, course=course).exists():
        return True
    try:
        sub = user.subscription_owner
        if sub.is_active and sub.end_date > timezone.now():
            return True
    except ObjectDoesNotExist:
        pass
    
    shared_subs = user.shared_subscriptions.filter(is_active=True, end_date__gt=timezone.now(), plan__name="family")
    if shared_subs.exists():
        return True
    return False

@login_required
def student_verify(request):
    existing = StudentVerification.objects.filter(user=request.user).order_by("-submitted_at").first()
    if existing and existing.status == "pending":
        messages.info(request, "Ваш запит на верифікацію вже на перевірці.")
        return redirect("index")

    if request.method == "POST":
        photo = request.FILES.get("document_photo")
        if not photo:
            messages.error(request, "Будь ласка, завантажте фото документа.")
            return redirect("student_verify")
        StudentVerification.objects.create(user=request.user, document_photo=photo)
        messages.success(request, "Документ надіслано на перевірку!")
        return redirect("index")

    return render(request, "main/student_verify.html", {"existing": existing})

@login_required
@require_http_methods(["POST"])
def add_friend(request):
    """Додавання друга до сімейної підписки"""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        User = get_user_model()

        if not email and not username:
            messages.error(request, "Вкажіть Email або логін користувача.")
            return redirect("family_manage")

        friend = None
        if email and username:
            friend = User.objects.filter(email=email, username=username).first()
            if not friend:
                messages.error(
                    request,
                    "Користувача з таким поєднанням Email та логіна не знайдено.",
                )
                return redirect("family_manage")
        elif email:
            friend = User.objects.filter(email=email).first()
            if not friend:
                messages.error(request, "Користувача з таким Email не знайдено.")
                return redirect("family_manage")
        elif username:
            friend = User.objects.filter(username=username).first()
            if not friend:
                messages.error(request, "Користувача з таким логіном не знайдено.")
                return redirect("family_manage")
            
        if friend == request.user:
            messages.error(request, "Ви не можете додати самого себе.")
            return redirect("family_manage")

        subscription = _get_active_family_subscription(request.user)
        if not subscription:
            messages.error(
                request,
                "У вас немає активної сімейної підписки.",
            )
            return redirect("profile")

        if not subscription.has_member_slot():
            messages.error(
                request,
                f"Досягнуто ліміт друзів (максимум {subscription.MAX_MEMBERS}).",
            )
            return redirect("family_manage")

        if subscription.members.filter(id=friend.id).exists():
            messages.info(request, "Цей користувач вже доданий до підписки.")
            return redirect("family_manage")
            
        subscription.members.add(friend)
        messages.success(
            request,
            (
                f"Користувача {friend.username} додано. "
                "Відтепер він має доступ до всіх преміум-курсів за вашою сімейною підпискою."
            ),
        )
        
    return redirect("family_manage")


@login_required
def family_manage(request):
    family = _get_active_family_subscription(request.user)
    if not family:
        messages.error(request, "У вас немає активної сімейної підписки.")
        return redirect("profile")
    return render(request, "main/family_manage.html", {"family": family})


@login_required
@require_http_methods(["POST"])
def family_remove_member(request, member_id):
    family = _get_active_family_subscription(request.user)
    if not family:
        messages.error(request, "У вас немає активної сімейної підписки.")
        return redirect("profile")

    member = get_object_or_404(get_user_model(), id=member_id)
    if not family.members.filter(id=member.id).exists():
        messages.error(request, "Цей користувач не є учасником вашої підписки.")
        return redirect("family_manage")

    family.members.remove(member)
    messages.success(request, f"{member.username} видалено з сімейної підписки.")
    return redirect("family_manage")


@login_required
def subscribe(request, plan_id):
    """Замість оформлення, додаємо підписку в кошик."""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # Не дозволяємо купувати той самий активний план повторно
    active_sub = _get_active_owned_subscription(request.user)
    if active_sub and active_sub.plan and active_sub.plan.name == plan.name:
        messages.info(
            request,
            f"Підписка «{plan.get_name_display()}» у вас вже є.",
        )
        return redirect("index")

    # Якщо користувач вже учасник сімейної підписки, не купуємо family ще раз
    if (
        plan.name == "family"
        and request.user.shared_subscriptions.filter(
            is_active=True,
            end_date__gt=timezone.now(),
            plan__name="family",
        ).exists()
    ):
        messages.info(
            request,
            "У вас вже є доступ до сімейної підписки як учасника.",
        )
        return redirect("index")

    if plan.name == "student":
        sv = StudentVerification.objects.filter(
            user=request.user, status="approved"
        ).first()
        if not sv:
            messages.error(request, "Спершу підтвердіть свій студентський статус.")
            return redirect("student_verify")

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, plan=plan
    )

    messages.success(request, f"Підписку «{plan.get_name_display()}» додано до кошика!")
    return redirect("cart_detail")
