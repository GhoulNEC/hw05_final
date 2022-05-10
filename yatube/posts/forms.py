from django import forms

from .models import Comment, Post, User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст поста', 'group': 'Группа',
                  'image': 'Картинка'}
        help_texts = {'text': 'Добавьте текст', 'group': 'Группа поста',
                      'image': 'Картинка поста'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий'}
        help_texts = {'text': 'прокомментируйте пост'}


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'birth_date', 'avatar',
                  'city')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
            'birth_date': 'Дата рождения',
            'avatar': 'Фото профиля',
            'city': 'Место рождения'
        }
        help_texts = {
            'first_name': 'Введите имя',
            'last_name': 'Введите фамилию',
            'email': 'Введите электронную почту',
            'birth_date': 'Введите дату рождения',
            'avatar': 'Загрузите картинку для профиля',
            'city': 'Укажите город',
        }
