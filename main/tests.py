from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase

from .models import CartItem, ContactMessage, Course, Enrollment, LessonProgress, Profile, Review


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.course = Course.objects.create(
            title='Основи інвестицій',
            description='Тестовий опис курсу.',
            category='investing',
            price=Decimal('100.00'),
            is_premium=True
        )

    def test_course_creation(self):
        """Тест створення моделі Course"""
        self.assertEqual(self.course.title, 'Основи інвестицій')
        self.assertEqual(self.course.price, Decimal('100.00'))
        self.assertEqual(str(self.course), 'Основи інвестицій')
        self.assertTrue(self.course.is_active)

    def test_profile_auto_created(self):
        """Тест автоматичного створення профілю при реєстрації (сигнали)"""
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertEqual(str(self.user.profile), 'testuser Profile')

    def test_cart_item_creation(self):
        """Тест додавання курсу в кошик"""
        cart_item = CartItem.objects.create(user=self.user, course=self.course)
        self.assertEqual(cart_item.user, self.user)
        self.assertEqual(cart_item.course, self.course)
        self.assertIn('Cart:', str(cart_item))

    def test_review_creation(self):
        """Тест створення відгуку"""
        review = Review.objects.create(
            user=self.user,
            course=self.course,
            text='Чудовий курс!',
            rating=5
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, 'Чудовий курс!')
        self.assertFalse(review.is_approved)

    def test_enrollment_creation(self):
        """Тест зарахування на курс"""
        enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        self.assertEqual(enrollment.user, self.user)
        self.assertEqual(enrollment.course, self.course)
        self.assertFalse(enrollment.is_completed)

    def test_contact_message(self):
        """Тест моделі для форми контактів"""
        msg = ContactMessage.objects.create(
            name='Іван',
            email='ivan@example.com',
            subject='Питання',
            message='Привіт!'
        )
        self.assertEqual(msg.name, 'Іван')
        self.assertEqual(msg.email, 'ivan@example.com')
        self.assertIn('Питання', str(msg))


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.free_course = Course.objects.create(
            title='Безкоштовний Курс',
            description='Опис безкоштовного курсу.',
            category='general',
            price=Decimal('0.00'),
            is_premium=False
        )

    def test_index_view(self):
        """Тест доступу до головної сторінки"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index.html')

    def test_courses_view(self):
        """Тест сторінки каталогу курсів"""
        response = self.client.get('/courses/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/courses.html')

    def test_course_detail_view(self):
        """Тест сторінки деталей курсу"""
        response = self.client.get(f'/course/{self.free_course.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/course_detail.html')

    def test_about_view(self):
        """Тест сторінки 'Про нас'"""
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/about.html')

    def test_contact_view(self):
        """Тест сторінки контактів"""
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/contact.html')

    def test_profile_view_requires_login(self):
        """Профіль повинен бути закритим для анонімів"""
        response = self.client.get('/profile/')
        # Переадресація на сторінку логіну
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_profile_view_logged_in(self):
        """Доступ до профілю авторизованим користувачам"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/profile.html')

    def test_add_to_cart_ajax(self):
        """Тест AJAX-обробника для додавання в кошик"""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(f'/add-to-cart/{self.free_course.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CartItem.objects.filter(user=self.user, course=self.free_course).exists())
        self.assertEqual(response.json()['success'], True)

class CartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.course = Course.objects.create(
            title='Тест Кошика',
            description='Курс для кошика.',
            category='general',
            price=Decimal('50.00'),
            is_premium=True
        )

    def test_cart_detail_view(self):
        """Тест рендерингу сторінки кошика"""
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/cart.html')

    def test_remove_from_cart(self):
        """Тест видалення з кошика"""
        self.client.login(username='testuser', password='password123')
        item = CartItem.objects.create(user=self.user, course=self.course)
        
        response = self.client.post(f'/cart/remove/{item.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())