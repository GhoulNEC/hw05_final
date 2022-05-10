from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='test_comment'
        )

    def setUp(self):
        self.user_2 = User.objects.create_user(username='test_user_2')
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_2)
        self.url_names_reverse_names = (
            ('posts:index', None, '/'),
            ('posts:group_list', (self.group.slug,),
             f'/group/{self.group.slug}/'),
            ('posts:profile', (self.user,), f'/profile/{self.user}/'),
            ('posts:edit_profile', (self.user,),
             f'/profile/{self.user}/edit/'),
            ('posts:post_detail', (self.post.id,), f'/posts/{self.post.id}/'),
            ('posts:post_create', None, '/create/'),
            ('posts:post_edit', (self.post.id,),
             f'/posts/{self.post.id}/edit/'),
            ('posts:follow_index', None, '/follow/'),
            ('posts:add_comment', (self.post.id,),
             f'/posts/{self.post.id}/comment/'),
            ('posts:edit_comment', (self.comment.id,),
             f'/posts/comment/{self.comment.id}/edit/'),
            ('posts:delete_comment', (self.comment.id,),
             f'/posts/comment/{self.comment.id}/delete/'),
            ('posts:profile_follow', (self.user_2,),
             f'/profile/{self.user_2}/follow/'),
            ('posts:profile_unfollow', (self.user_2,),
             f'/profile/{self.user_2}/unfollow'),
            ('posts:post_delete', (self.post.id,),
             f'/posts/{self.post.id}/delete/')
        )

    def test_post_url_url_name_equal_reverse_names(self):
        """URL-адреса идентичны их name_space"""
        for reverse_name, arg, address in self.url_names_reverse_names:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse(reverse_name, args=arg), address)

    def test_unexisting_page(self):
        """Запрос к несуществующей странице /unexisting_page/
        вернет ошибку 404
        """
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_page_not_found_uses_custom_template(self):
        """Страница 404 отдает кастомный шаблон"""
        response = self.client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_posts_post_id_edit_url_exists_desired_location_post_author(self):
        """Страницы /posts/self.post.id/edit/,
        /posts/self.post.id/delete /comment/edit/ перенаправляют пользователя,
        если он не является автором.
        """
        for reverse_name, arg, _ in self.url_names_reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse(reverse_name, args=arg))
                if reverse_name in 'posts:post_edit':
                    self.assertRedirects(response, reverse(
                        'posts:post_detail', args=arg))
                elif reverse_name in ['posts:add_comment',
                                      'posts:profile_follow',
                                      'posts:profile_unfollow',
                                      'posts:delete_comment']:
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                elif reverse_name in ['posts:post_delete',
                                      'posts:edit_comment']:
                    self.assertRedirects(response, reverse(
                        'posts:post_detail', args=(self.post.id,)))
                elif reverse_name in 'posts:edit_profile':
                    self.assertRedirects(response, reverse(
                        'posts:profile', args=(self.user,)))
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_create_and_edit_redirects_guest_client(self):
        """Страницы /create/, /edit/, /delete/, /comment/, /comment/delete/,
        /follow/, /unfollow/ перенаправляют анонимного пользователя
        на страницу логина
        """
        login_redirect = '/auth/login/?next='
        for reverse_name, arg, _ in self.url_names_reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse(reverse_name, args=arg))
                if reverse_name in ['posts:post_create', 'posts:post_edit',
                                    'posts:post_delete', 'posts:add_comment',
                                    'posts:delete_comment',
                                    'posts:profile_follow',
                                    'posts:profile_unfollow',
                                    'posts:edit_comment',
                                    'posts:edit_profile']:
                    self.assertRedirects(
                        response,
                        login_redirect + reverse(reverse_name, args=arg))
                elif reverse_name in 'posts:follow_index':
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_available_to_author(self):
        """Все URL-адреса доступны автору поста,
        страницы /follow/ и /unfollow/ доступны авторизованному пользователю.
        """
        for reverse_name, arg, _ in self.url_names_reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(
                    reverse(reverse_name, args=arg))
                if reverse_name in ['posts:profile_follow',
                                    'posts:profile_unfollow']:
                    response = self.authorized_client.get(
                        reverse(reverse_name, args=arg)
                    )
                    self.assertRedirects(response, reverse(
                        'posts:profile', args=(self.user_2,)))
                elif reverse_name in 'posts:add_comment':
                    response = self.author_client.get(
                        reverse(reverse_name, args=arg),
                        data={'text': 'test_comment'},
                        follow=True
                    )
                    self.assertRedirects(response, reverse(
                        'posts:post_detail', args=(self.post.id,)))
                elif reverse_name in 'posts:delete_comment':
                    self.assertRedirects(response, reverse(
                        'posts:post_detail', args=(self.post.id,)))
                elif reverse_name in 'posts:post_delete':
                    self.assertRedirects(response, reverse(
                        'posts:profile', args=(self.user,)))
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
