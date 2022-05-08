from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User


class UsersURLTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.url_names_reverse_names = (
            ('users:signup', '/auth/signup/', 'users/signup.html'),
            ('users:login', '/auth/login/', 'users/login.html'),
            ('users:logout', '/auth/logout/', 'users/logged_out.html'),
            ('users:password_change', '/auth/password_change/',
             'users/password_change_form.html'),
            ('users:password_reset_form', '/auth/password_reset/',
             'users/password_reset_form.html')
        )

    def test_users_url_name_equal_reverse_names(self):
        """URL-адреса идентичны их name_space"""
        for reverse_name, address, _ in self.url_names_reverse_names:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse(reverse_name), address)

    def test_auth_url_exists_at_desired_location(self):
        """Проверка доступности адресов /auth/ для анонимных пользователей"""
        url_names = '/auth/signup/', '/auth/login/', '/auth/password_reset/', \
                    '/auth/password_reset/done/'
        for address in url_names:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_url_exists_at_desired_location_authorized(self):
        """Проверка доступности адреса/auth/logout/ для зарегистрированных
        пользователей
        """
        response = self.authorized_client.get('/auth/logout/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        url_names_templates = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Страницы по адресам /auth/password_change/ и
        /auth/password_change_done/ перенаправляют
        анонимного пользователя на страницу логина
        """
        url_names_redirects = {
            '/auth/password_change/':
                '/auth/login/?next=/auth/password_change/',
            '/auth/password_change/done/':
                '/auth/login/?next=/auth/password_change/done/'
        }
        for address, redirect in url_names_redirects.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertRedirects(response, redirect)
