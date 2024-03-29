from django.contrib.auth.models import AbstractUser
from django.db import models

from mptt.models import MPTTModel, TreeForeignKey


class User(AbstractUser):
    access_rights = (
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('user', 'Пользователь')
    )
    birth_date = models.DateField('Дата рождения', blank=True, null=True)
    avatar = models.ImageField('Аватарка', upload_to='profile/',
                               blank=True, null=True)
    city = models.CharField('Город', max_length=30, blank=True, null=True)
    permission = models.CharField('Тип пользователя', max_length=30,
                                  choices=access_rights, blank=True, null=True)


class Group(models.Model):
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Наименование slug', unique=True)
    description = models.TextField('Описание')

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(MPTTModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    text = models.TextField('Текст комментария',
                            help_text='Прокомментируйте пост')
    created = models.DateTimeField('Дата комментария', auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ('-created',)


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following', verbose_name='Автор')

    class Meta:
        ordering = ('author',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
