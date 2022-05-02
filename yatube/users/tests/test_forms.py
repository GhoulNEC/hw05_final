from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UsersCreationFormTest(TestCase):
    def test_create_new_user(self):
        """Создание нового пользователя"""
        form_data = {
            'first_name': 'test_name',
            'last_name': 'test_surname',
            'username': 'new_user',
            'email': 'test_email@test.com',
            'password1': 'test_pass',
            'password2': 'test_pass',
        }

        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        created_user = User.objects.get()
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(created_user.username, 'new_user')
