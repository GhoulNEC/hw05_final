from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutURLTests(TestCase):
    def test_about_url_url_name_equal_reverse_names(self):
        """URL-адреса идентичны их name_space"""
        url_names_reverse_names = (('/about/author/', 'about:author'),
                                   ('/about/tech/', 'about:tech'))
        for address, reverse_name in url_names_reverse_names:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(address, reverse(reverse_name))

    def test_author_url_exists_at_desired_location(self):
        """Проверка доступности URL-адресов"""
        url_names = 'about:author', 'about:tech'
        for reverse_name in url_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse(reverse_name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_names_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон"""
        about_names_templates = (('about:author', 'about/author.html'),
                                 ('about:tech', 'about/tech.html'))
        for reverse_name, template in about_names_templates:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse(reverse_name))
                self.assertTemplateUsed(response, template)
