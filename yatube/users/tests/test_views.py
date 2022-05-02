from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

User = get_user_model()


class UsersViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.guest_client = Client()
        self.authorizes_client = Client()
        self.authorizes_client.force_login(self.user)

    def test_users_names_uses_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны"""
        users_names_templates = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
        }
        for reverse_name, template in users_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_users_names_uses_correct_password_reset_templates(self):
        """URL-адреса для восстановления пароля по почте
        используют соответствующие шаблоны
        """
        users_names_templates = {
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html'
        }
        for reverse_name, template in users_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
