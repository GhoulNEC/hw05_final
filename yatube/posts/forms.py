from django import forms

from .models import Comment, Post


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
