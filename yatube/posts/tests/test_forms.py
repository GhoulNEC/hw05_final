import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок - 2',
            slug='test_slug_2',
            description='Тестовое описание - 2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_post',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый пост формы',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_2 = Post.objects.first()
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post_2.text, 'Тестовый пост формы')
        self.assertEqual(post_2.author, self.user)
        self.assertEqual(post_2.group, self.group)
        self.assertTrue(Post.objects.filter(
            image='posts/small.gif').exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_author(self):
        """Автор поста может его редактировать"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный пост формы',
            'group': self.group_2.id
        }
        response_1 = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id},
                    ),
            data=form_data,
            follow=True
        )
        edited_text = Post.objects.first()
        response_2 = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        self.assertEqual(response_1.status_code, HTTPStatus.OK)
        self.assertEqual(edited_text.text, 'Измененный пост формы')
        self.assertEqual(edited_text.group, self.group_2)
        self.assertEqual(edited_text.author, self.user)
        self.assertEqual(response_2.status_code, HTTPStatus.OK)
        self.assertEqual(len(response_2.context.get(
            'page_obj').object_list), 0)
        self.assertEqual(posts_count, Post.objects.count())
        self.assertRedirects(response_1,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))

    def test_create_post_guest_client(self):
        """Анонимный пользователь не может создавать пост"""
        posts_count = Post.objects.count()
        response = self.client.get(reverse('posts:post_create'))
        posts_count_create = Post.objects.count()
        login_redirect = '/auth/login/?next='
        self.assertEqual(posts_count, posts_count_create)
        self.assertRedirects(response,
                             login_redirect + reverse('posts:post_create'))
