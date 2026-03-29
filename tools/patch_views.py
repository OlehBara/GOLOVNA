import re
import os

BASE_DIR = r"c:\Users\User\OneDrive\Робочий стіл\Django_Lipa\DIPLOM"

# 1. Update views.py
views_path = os.path.join(BASE_DIR, "main", "views.py")
with open(views_path, "r", encoding="utf-8") as f:
    views_content = f.read()

# Fix imports
views_content = views_content.replace(
    "Enrollment, FamilyGroup,",
    "Enrollment,"
)
from_exceptions = "from django.core.exceptions import ObjectDoesNotExist\n"
if from_exceptions not in views_content:
    views_content = views_content.replace(
        "from django.db import models\n",
        "from django.db import models\n" + from_exceptions
    )

# Fix profile_view
profile_view_old = """@login_required
def profile_view(request):
    \"\"\"Особистий кабінет користувача\"\"\"
    # Активні курси (ще не завершені)
    user_courses = Enrollment.objects.filter(
        user=request.user, is_completed=False, course__is_premium=True
    ).select_related("course")

    # Пройдені курси (завершені)
    completed_courses = Enrollment.objects.filter(
        user=request.user, is_completed=True
    ).select_related("course")

    context = {
        "display_name": request.user.username,
        "display_email": request.user.email,
        "user_courses": user_courses,
        "completed_courses": completed_courses,
    }
    return render(request, "main/profile.html", context)"""

profile_view_new = """@login_required
def profile_view(request):
    \"\"\"Особистий кабінет користувача\"\"\"
    user_courses = Enrollment.objects.filter(
        user=request.user, is_completed=False, course__is_premium=True
    ).select_related("course")

    completed_courses = Enrollment.objects.filter(
        user=request.user, is_completed=True
    ).select_related("course")

    try:
        subscription = request.user.subscription_owner
    except ObjectDoesNotExist:
        subscription = None

    context = {
        "display_name": request.user.username,
        "display_email": request.user.email,
        "user_courses": user_courses,
        "completed_courses": completed_courses,
        "subscription": subscription,
    }
    return render(request, "main/profile.html", context)"""

views_content = views_content.replace(profile_view_old, profile_view_new)

# Fix cart_detail
cart_detail_old_regex = r"def cart_detail\(request\):[\s\S]*?total_price = sum\(item\.course\.price for item in cart_items\)[\s\S]*?return render\(request, \"main/cart\.html\", context\)"

def cart_detail_repl(m):
    return """def cart_detail(request):
    \"\"\"Сторінка кошика\"\"\"
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

    total_price = 0
    for item in cart_items:
        if item.course:
            total_price += item.course.price
        elif item.plan:
            total_price += item.plan.price

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, "main/cart.html", context)"""

views_content = re.sub(cart_detail_old_regex, cart_detail_repl, views_content)

# Fix checkout & process_payment & payment_success
# Wait, for checkout:
checkout_regex = r"def checkout\(request\):[\s\S]*?total_price = sum\(item\.course\.price for item in cart_items\)[\s\S]*?return render\(request, \"main/payment\.html\", context\)"

def checkout_repl(m):
    return """def checkout(request):
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

    total_price = 0
    for item in cart_items:
        if item.course:
            total_price += item.course.price
        elif item.plan:
            total_price += item.plan.price

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
    }
    return render(request, "main/payment.html", context)"""
views_content = re.sub(checkout_regex, checkout_repl, views_content)

process_payment_old = """@login_required
@require_http_methods(["POST"])
def process_payment(request):
    \"\"\"
    Fake payment processing:
    - Enroll user in every course from the cart
    - Clear the cart
    - Redirect to profile with a success message
    \"\"\"
    cart_items = CartItem.objects.filter(user=request.user).select_related("course")

    enrolled_count = 0
    for item in cart_items:
        Enrollment.objects.get_or_create(user=request.user, course=item.course)
        enrolled_count += 1

    cart_items.delete()

    if enrolled_count:
        messages.success(
            request,
            f"✅ Оплата успішна! Ви отримали доступ до {enrolled_count} курс(ів).",
        )
    else:
        messages.info(request, "Кошик був порожній — нічого не оплачено.")

    return redirect("profile")


@login_required
def payment_success(request):
    \"\"\"
    Confirm payment and enroll the user in all cart courses.

    Steps:
    1. Fetch all CartItem records for the current user.
    2. Create an Enrollment for each course (get_or_create avoids duplicates).
    3. Delete all CartItem records — clears the cart.
    4. Redirect to the profile page where enrolled courses are listed.

    After this view runs:
    - The "Купити" button on course_detail will show "Вже куплено"
      because `is_enrolled` is checked via Enrollment.objects.filter(...).exists()
    - The cart badge count drops to 0.
    \"\"\"
    cart_items = CartItem.objects.filter(user=request.user).select_related("course")

    enrolled_count = 0
    for item in cart_items:
        Enrollment.objects.get_or_create(user=request.user, course=item.course)
        enrolled_count += 1

    # Clear the cart
    cart_items.delete()

    if enrolled_count:
        messages.success(
            request,
            f"🎉 Вітаємо! Ви успішно придбали {enrolled_count} курс(ів). Приємного навчання!",
        )
    else:
        messages.info(request, "Кошик був порожній.")

    return redirect("profile")"""

process_payment_new = """@login_required
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

    return redirect("profile")"""

views_content = views_content.replace(process_payment_old, process_payment_new)

# Subscriptions Section Replace
subs_re = r"def has_course_access\(user, course\):[\s\S]*?(?=# ─── Course 1: Основи бюджетування ───────────────────────────────────────────)"

subs_new = """def has_course_access(user, course):
    \"\"\"Перевіряє чи має користувач доступ до курсу.\"\"\"
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
def add_friend(request):
    \"\"\"Додавання друга до сімейної підписки\"\"\"
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            friend = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Користувача з таким Email не знайдено.")
            return redirect("profile")
            
        if friend == request.user:
            messages.error(request, "Ви не можете додати самого себе.")
            return redirect("profile")

        try:
            subscription = request.user.subscription_owner
        except ObjectDoesNotExist:
            messages.error(request, "У вас немає активної підписки.")
            return redirect("profile")
            
        if subscription.plan.name != "family":
            messages.error(request, "Ця функція доступна лише для Сімейної підписки.")
            return redirect("profile")

        if subscription.members.count() >= 3:
            messages.error(request, "Досягнуто ліміт друзів (максимум 3).")
            return redirect("profile")
            
        subscription.members.add(friend)
        messages.success(request, f"Користувача {friend.username} додано до вашої сімейної підписки!")
        
    return redirect("profile")


@login_required
def subscribe(request, plan_id):
    \"\"\"Замість оформлення, додаємо підписку в кошик.\"\"\"
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

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

"""

views_content = re.sub(subs_re, subs_new, views_content)

with open(views_path, "w", encoding="utf-8") as f:
    f.write(views_content)


# 2. Update urls.py
urls_path = os.path.join(BASE_DIR, "main", "urls.py")
with open(urls_path, "r", encoding="utf-8") as f:
    urls_content = f.read()

urls_content = urls_content.replace(
    'path("subscriptions/family/", views.family_manage, name="family_manage"),',
    'path("profile/add-friend/", views.add_friend, name="add_friend"),'
)
urls_content = urls_content.replace(
    'path(\n        "subscriptions/family/remove/<int:user_id>/",\n        views.family_remove_member,\n        name="family_remove_member",\n    ),',
    ''
)
with open(urls_path, "w", encoding="utf-8") as f:
    f.write(urls_content)

print("Patch applied to views.py and urls.py")
