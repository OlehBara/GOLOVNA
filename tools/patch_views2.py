import re
import os

BASE_DIR = r"c:\Users\User\OneDrive\Робочий стіл\Django_Lipa\DIPLOM"
views_path = os.path.join(BASE_DIR, "main", "views.py")

with open(views_path, "r", encoding="utf-8") as f:
    views_content = f.read()

subs_re = r"def has_course_access\(user, course\):[\s\S]*"

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

print("Patch applied to views.py end!")
