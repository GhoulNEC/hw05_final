import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_author'),
            text='Тестовый текст',
            group=Group.objects.create(
                title='Тестовый заголовок',
                slug='test_slug'
            ),
            image=uploaded
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок 2',
            slug='test_slug_2'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def test_posts_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        posts_names_templates = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list', (self.post.group.slug,),
             'posts/group_list.html'),
            ('posts:profile', (self.user,), 'posts/profile.html'),
            ('posts:post_detail', (self.post.id,), 'posts/post_detail.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:follow_index', None, 'posts/follow.html')
        )
        for reverse_name, arg, template in posts_names_templates:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(
                    reverse(reverse_name, args=arg))
                self.assertTemplateUsed(response, template)

    def test_posts_create_edit_urls_show_correct_context(self):
        """Шаблоны create и edit сформированы с правильным контекстом"""
        templates = (('posts:post_create', None),
                     ('posts:post_edit', (self.post.id,)))

        context = (('text', forms.fields.CharField),
                   ('group', forms.fields.ChoiceField),
                   ('image', forms.fields.ImageField))

        for reverse_name, arg in templates:
            with self.subTest(reverse_name=reverse_name):
                for value, expected in context:
                    with self.subTest(value=value):
                        response = self.authorized_author.get(
                            reverse(reverse_name, args=arg))
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(response.context['form'],
                                              PostForm)
                        self.assertIsInstance(form_field, expected)

    def posts_templates_show_correct_template(self, response, post,
                                              one_post=False):
        first_object = response.context['post'] if one_post \
            else response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        group_title_0 = first_object.group.title
        pub_date_0 = first_object.pub_date
        image_0 = first_object.image
        self.assertEqual(post_text_0, post.text)
        self.assertEqual(post_author_0, post.author)
        self.assertEqual(group_title_0, post.group.title)
        self.assertEqual(pub_date_0, post.pub_date)
        self.assertEqual(image_0, post.image)
        self.assertContains(response, '<img')

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.posts_templates_show_correct_template(response,
                                                   self.post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        self.posts_templates_show_correct_template(response, self.post)
        group_object = response.context['group']
        group_title = group_object.title
        group_slug = group_object.slug
        group_description = group_object.description
        self.assertEqual(group_object, self.post.group)
        self.assertEqual(group_title, self.post.group.title)
        self.assertEqual(group_slug, self.post.group.slug)
        self.assertEqual(group_description, self.post.group.description)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=(self.post.group.id,)))
        self.posts_templates_show_correct_template(response, self.post,
                                                   True)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'test_author'}))
        self.posts_templates_show_correct_template(response, self.post,
                                                   False)
        author_object = response.context['author']
        self.assertEqual(author_object, self.post.author)

    def test_post_do_not_get_to_another_group(self):
        """Пост не попал в группу, для которой не был предназначен"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group_2.slug}))
        self.assertEqual(len(response.context.get('page_obj').object_list), 0)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_delete_author(self):
        """Автор поста может его удалить"""
        post_count = Post.objects.count()
        response_1 = self.authorized_author.get(
            reverse('posts:post_delete', args=(self.post.id,))
        )
        post_count_delete = Post.objects.count()
        response_2 = self.authorized_author.get(reverse(
            'posts:profile', args=(self.post.author,)))
        self.assertEqual(post_count, 1)
        self.assertEqual(post_count_delete, 0)
        self.assertEqual(len(response_2.context.get(
            'page_obj').object_list), 0)
        self.assertEqual(response_1.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response_1, reverse('posts:profile',
                                                 args=(self.post.author,)))


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.author = User.objects.create(username='test_author')
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug'
        )
        self.post_amount = 13
        for post in range(self.post_amount):
            self.posts = Post.objects.create(
                text=f'Тестовый пост {post}',
                author=self.author,
                group=self.group
            )
        self.posts_names = (
            ('posts:index', None), ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.posts.author,))
        )

    def test_first_page_contains_ten_records(self):
        """Количество постов на первых страницах шаблонов должно быть 10"""
        for reverse_name, arg in self.posts_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse(reverse_name, args=arg))
                self.assertEqual(len(
                    response.context.get('page_obj').object_list),
                    settings.POSTS_LIMIT)

    def test_second_page_contains_ten_records(self):
        """Количество постов на вторых страницах шаблонов должно быть 3"""
        page_2 = '?page=2'
        first_page_posts_amount = settings.POSTS_LIMIT
        posts_difference = self.post_amount - first_page_posts_amount
        for reverse_name, arg in self.posts_names:
            with self.subTest(reverse_name=reverse_name):
                response_2 = self.client.get(reverse(reverse_name, args=arg)
                                             + page_2)
                self.assertEqual(len(
                    response_2.context.get('page_obj').object_list),
                    posts_difference)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_text'
        )

    def setUp(self):
        self.author = self.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_index_cache(self):
        """Страница index сохраняется в кэше"""
        post_count = Post.objects.count()
        post_2 = Post.objects.create(author=self.author, text='test_text_2')
        response_0 = self.authorized_client.get(reverse('posts:index'))
        objects_count_0 = len(response_0.context['page_obj'].object_list)
        first_object_0 = response_0.context['page_obj'][0]
        post_text_0 = first_object_0.text
        post_author_0 = first_object_0.author
        self.assertEqual(objects_count_0, post_count + 1)
        self.assertEqual(post_text_0, post_2.text)
        self.assertEqual(post_author_0, post_2.author)
        Post.objects.filter(id=post_2.id).delete()
        response_1 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_0.content, response_1.content)
        cache.clear()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_0.content, response_2.content)


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_text'
        )

    def setUp(self):
        self.author = self.post.author
        self.user = User.objects.create_user(username='test_user')
        self.follower_user = User.objects.create_user(username='test_follower')
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower = Client()
        self.follower.force_login(self.follower_user)

    def test_follow_authorized_client(self):
        """Авторизованный пользователь может подписываться на
        других пользователей и удалять их из подписок
        """
        subscriptions_count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', args=(self.author.username,))
        )
        self.assertEqual(subscriptions_count, 0)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), subscriptions_count + 1)
        response_2 = self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(self.author.username,))
        )
        self.assertEqual(response_2.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), subscriptions_count)

    def test_new_post_appears_in_follower_post_list_and_not_in_user(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        posts_count = Post.objects.count()
        Follow.objects.create(user=self.follower_user, author=self.author)
        response_follow = self.follower.get(reverse('posts:follow_index'))
        objects_count_follow = len(
            response_follow.context['page_obj'].object_list)
        response_create = self.author_client.post(
            reverse('posts:post_create'),
            data={'text': 'test_new_post'},
            follow=True
        )
        response_follow_2 = self.follower.get(reverse('posts:follow_index'))
        objects_count_follow_2 = len(
            response_follow_2.context['page_obj'].object_list)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        objects_count = len(
            response.context['page_obj'].object_list)
        self.assertEqual(objects_count_follow, 1)
        self.assertEqual(response_create.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(objects_count_follow_2, 2)
        self.assertEqual(objects_count, 0)


class CommentViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_author'),
            text='Тестовый текст',
            group=Group.objects.create(
                title='Тестовый заголовок',
                slug='test_slug'
            )
        )

    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.user_2 = User.objects.create_user(username='test_user_2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_post_comment_authorized_client(self):
        """Комментировать пост может только авторизованный пользователь"""
        comments_count = Comment.objects.count()
        response_1 = self.client.post(
            reverse('posts:add_comment', args=(self.post.id,)))
        login_redirect = '/auth/login/?next='
        self.assertRedirects(
            response_1, login_redirect + reverse('posts:add_comment',
                                                 args=(self.post.id,)))
        self.assertEqual(self.post.comments.count(), comments_count)
        response_2 = self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data={'text': 'test-comment'},
            follow=True
        )
        self.assertEqual(response_2.status_code, HTTPStatus.OK)
        self.assertEqual(self.post.comments.count(), comments_count + 1)

    def test_post_delete_comment_post_author_or_comment_author(self):
        """Удалять комментарии может только автор посла и автор комментария"""
        comment_0 = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='test_comment'
        )
        comment_1 = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='test_comment_2'
        )
        comment_2 = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='test_comment_3'
        )
        comments_count = Comment.objects.count()
        response_0 = self.authorized_author.get(reverse(
            'posts:delete_comment', args=(comment_0.id,)))
        comments_count_0 = Comment.objects.count()
        response_1 = self.authorized_client.get(reverse(
            'posts:delete_comment', args=(comment_1.id,)))
        comments_count_1 = Comment.objects.count()
        response_2 = self.authorized_client_2.get(reverse(
            'posts:delete_comment', args=(comment_2.id,)))
        comments_count_2 = Comment.objects.count()
        self.assertEqual(response_0.status_code, HTTPStatus.FOUND)
        self.assertEqual(comments_count_0, comments_count - 1)
        self.assertEqual(response_1.status_code, HTTPStatus.FOUND)
        self.assertEqual(comments_count_1, comments_count_0 - 1)
        self.assertEqual(response_1.status_code, HTTPStatus.FOUND)
        self.assertEqual(comments_count_2, comments_count_1)

    def test_edit_comment(self):
        """Редактировать комментарий, может только автор комментария"""
        comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='test_comment'
        )
        comments_count = Comment.objects.count()
        form_data = {'text': 'edited_comment'}
        response_0 = self.authorized_client.post(reverse(
            'posts:edit_comment', args=(comment.id,)),
            data=form_data,
            follow=True
        )
        comments_count_0 = Comment.objects.count()
        edited_comment_0 = Comment.objects.get(id=comment.id)
        response_1 = self.authorized_client_2.post(reverse(
            'posts:edit_comment', args=(comment.id,)),
            data=form_data,
            follow=True
        )
        comments_count_1 = Comment.objects.count()
        edited_comment_1 = Comment.objects.get(id=comment.id)
        self.assertEqual(response_0.status_code, HTTPStatus.OK)
        self.assertEqual(edited_comment_0.text, 'edited_comment')
        self.assertEqual(comments_count, comments_count_0)
        self.assertRedirects(response_0, reverse(
            'posts:post_detail', args=(self.post.id,)))
        self.assertEqual(comments_count, comments_count_1)
        self.assertNotEqual(edited_comment_1, 'edited_comment')
        self.assertRedirects(response_1, reverse(
            'posts:post_detail', args=(self.post.id,)))
