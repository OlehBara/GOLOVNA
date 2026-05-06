from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Електронна пошта", required=True)

    class Meta:
        model = User
        fields = ("username", "email")


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="Електронна пошта", required=True)

    class Meta:
        model = User
        fields = ["username", "email"]


from .models import Profile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image"]


from .models import Course


class CourseForm(forms.ModelForm):
    """Форма для створення/редагування курсу (тільки для адміна)"""

    class Meta:
        model = Course
        fields = [
            "title",
            "description",
            "price",
            "category",
            "rating",
            "is_active",
            "is_premium",
        ]
        labels = {
            "title": "Назва курсу",
            "description": "Опис",
            "price": "Ціна (грн)",
            "category": "Категорія",
            "rating": "Рейтинг",
            "is_active": "Активний",
            "is_premium": "Преміум",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Назва курсу"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-input", "rows": 4, "placeholder": "Опис курсу"}
            ),
            "price": forms.NumberInput(attrs={"class": "form-input", "min": "0"}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "rating": forms.NumberInput(
                attrs={"class": "form-input", "min": "0", "max": "5", "step": "0.1"}
            ),
        }
