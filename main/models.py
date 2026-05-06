from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Course(models.Model):
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=False)
    category = models.CharField(
        max_length=50,
        choices=[
            ("budgeting", "Budgeting"),
            ("investing", "Investing"),
            ("credit", "Credit"),
            ("pension", "Pension"),
            ("general", "General"),
        ],
        default="general",
    )
    rating = models.DecimalField(
        max_digits=3, decimal_places=1, null=False, default=0.0
    )
    is_active = models.BooleanField(null=False, default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "main_course"
        indexes = [
            models.Index(fields=["category"], name="idx_course_category"),
            models.Index(fields=["created_at"], name="idx_course_created_at"),
        ]

    def __str__(self):
        return self.title


class CartItem(models.Model):
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, null=True, blank=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    plan = models.ForeignKey('SubscriptionPlan', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True  # Django сам створить цю таблицю
        db_table = "main_cartitem"
        indexes = [
            models.Index(fields=["session_key"], name="idx_cart_session"),
            models.Index(fields=["user"], name="idx_cart_user"),
        ]

    def __str__(self):
        if self.course:
            return f"Cart: {self.course.title}"
        elif self.plan:
            return f"Cart: {self.plan.name}"
        return "Cart Item"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    text = models.TextField(null=False)
    rating = models.PositiveSmallIntegerField(
        null=False, default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_approved = models.BooleanField(null=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "main_review"
        unique_together = ("user", "course")
        indexes = [
            models.Index(fields=["course"], name="idx_review_course"),
            models.Index(fields=["user"], name="idx_review_user"),
            models.Index(fields=["rating"], name="idx_review_rating"),
            models.Index(fields=["created_at"], name="idx_review_created_at"),
        ]

    def __str__(self):
        return f"{self.display_name} - {self.rating}"

    @property
    def display_name(self):
        full_name = (self.user.get_full_name() or "").strip()
        return full_name or self.user.username

    @property
    def initials(self):
        name = (self.display_name or "").strip()
        if not name:
            return "??"
        parts = [p for p in name.split() if p]
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return parts[0][:2].upper()


class ContactMessage(models.Model):
    sender = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_messages",
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=200, blank=True, default="")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "main_contactmessage"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject or 'без теми'}"


class Profile(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")

    def __str__(self):
        return f"{self.user.username} Profile"


class Enrollment(models.Model):
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = "main_enrollment"
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.username} → {self.course.title}"


class LessonProgress(models.Model):
    STATUS_CHOICES = [
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    lesson_key = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="completed"
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "main_lessonprogress"
        unique_together = ("user", "course", "lesson_key")

    def __str__(self):
        return f"{self.user.username} -> {self.course.title} [{self.lesson_key}]"


class ChatMessage(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    chat_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="support_chat_messages",
    )
    message = models.TextField()
    is_admin_reply = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "main_chatmessage"
        ordering = ["timestamp"]


    def __str__(self):
        return f"{self.sender} → {self.chat_user}: {self.message[:30]}"


# ── Subscription System ──────────────────────────────────────────

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ("standard", "Standard"),
        ("family", "Family"),
        ("student", "Student"),
    ]

    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)

    class Meta:
        managed = True
        db_table = "main_subscriptionplan"

    def __str__(self):
        return f"{self.get_name_display()} – {self.price} грн"


class UserSubscription(models.Model):
    MAX_MEMBERS = 3

    owner = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="subscription_owner"
    )
    plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.SET_NULL, null=True, related_name="subscriptions"
    )
    members = models.ManyToManyField(
        User, blank=True, related_name="shared_subscriptions"
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = "main_usersubscription"

    def __str__(self):
        return f"{self.owner.username} – {self.plan}"

    def has_member_slot(self):
        return self.members.count() < self.MAX_MEMBERS


class StudentVerification(models.Model):
    STATUS_CHOICES = [
        ("pending", "На перевірці"),
        ("approved", "Підтверджено"),
        ("rejected", "Відхилено"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="student_verifications"
    )
    document_photo = models.ImageField(upload_to="verifications/")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = "main_studentverification"

    def __str__(self):
        return f"{self.user.username} – {self.get_status_display()}"


# ── Notification System ──────────────────────────────────────────

class Notification(models.Model):
    TYPE_CHOICES = [
        ("info", "Інформація"),
        ("success", "Успіх"),
        ("warning", "Попередження"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default="info"
    )
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "main_notification"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"


# ── Blog System ──────────────────────────────────────────────────

class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ("savings", "Заощадження"),
        ("investing", "Інвестиції"),
        ("budgeting", "Бюджетування"),
        ("credit", "Кредити"),
        ("tips", "Поради"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(max_length=500, help_text="Короткий опис для картки")
    content = models.TextField(help_text="Повний текст статті (HTML)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="tips")
    cover_emoji = models.CharField(max_length=10, default="📰", help_text="Емодзі для обкладинки")
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="blog_posts"
    )
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "main_blogpost"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def reading_time(self):
        """Estimated reading time in minutes"""
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))


# ── Certificate System ───────────────────────────────────────────

import uuid

class Certificate(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="certificates"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="certificates"
    )
    verification_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "main_certificate"
        unique_together = ("user", "course")

    def __str__(self):
        return f"Certificate: {self.user.username} – {self.course.title}"


# ── Signals ───────────────────────────────────────────────────────

from django.contrib.auth.models import User as AuthUser
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=AuthUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=AuthUser)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=StudentVerification)
def notify_student_approved(sender, instance, **kwargs):
    if instance.status == "approved":
        try:
            send_mail(
                subject="FinSmart – Ваш студентський статус підтверджено!",
                message=(
                    f"Вітаємо, {instance.user.username}!\n\n"
                    "Ваш студентський статус було успішно підтверджено. "
                    "Тепер ви можете придбати підписку за спеціальною студентською ціною.\n\n"
                    "З повагою,\nКоманда FinSmart"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=True,
            )
        except Exception:
            pass

@receiver(post_save, sender=Enrollment)
def notify_course_completed(sender, instance, **kwargs):
    if getattr(instance, 'is_completed', False):
        if not Notification.objects.filter(user=instance.user, message__icontains=instance.course.title).exists():
            Notification.objects.create(
                user=instance.user,
                message=f'Вітаємо! Ви успішно завершили курс "{instance.course.title}".',
                notification_type='success',
                link=f'/course/{instance.course.id}/'
            )

@receiver(post_save, sender=UserSubscription)
def notify_subscription_created(sender, instance, created, **kwargs):
    if created and getattr(instance, 'plan', None):
        Notification.objects.create(
            user=instance.owner,
            message=f'Ваша підписка "{instance.plan.get_name_display()}" успішно активована!',
            notification_type='success',
            link='/profile/'
        )
