from django.contrib import admin
from django.utils.html import format_html

from .models import (
    CartItem,
    ChatMessage,
    ContactMessage,
    Course,
    Enrollment,
    LessonProgress,
    Profile,
    Review,
    StudentVerification,
    SubscriptionPlan,
    UserSubscription,
)
admin.site.register(Course)
admin.site.register(Review)
admin.site.register(ContactMessage)
admin.site.register(LessonProgress)
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)
@admin.register(StudentVerification)
class StudentVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "submitted_at", "reviewed_at", "photo_thumbnail")
    list_filter = ("status",)
    list_editable = ("status",)
    readonly_fields = ("user", "document_photo", "submitted_at", "photo_preview")

    def photo_thumbnail(self, obj):
        if obj.document_photo:
            return format_html(
                '<img src="{}" style="max-height:50px; border-radius:4px;" />',
                obj.document_photo.url,
            )
        return "–"
    photo_thumbnail.short_description = "Фото"
    def photo_preview(self, obj):
        if obj.document_photo:
            return format_html(
                '<img src="{}" style="max-height:300px; border-radius:8px;" />',
                obj.document_photo.url,
            )
        return "–"
    photo_preview.short_description = "Попередній перегляд"
    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data and obj.status in ("approved", "rejected"):
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)



