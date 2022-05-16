from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (CommentForm, EditGroupsForm,
                    EditProfileForm, PostForm)
from .models import Comment, Follow, Group, Post, User
from .utils import get_page_obj


def index(request):
    posts = Post.objects.select_related('author', 'group').all()
    context = {
        'page_obj': get_page_obj(request, posts),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    context = {
        'group': group,
        'page_obj': get_page_obj(request, posts),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    following = request.user.is_authenticated and (Follow.objects.filter(
        user=request.user, author=author).exists())
    context = {
        'author': author,
        'page_obj': get_page_obj(request, posts),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


@login_required
def edit_profile(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        return redirect('posts:profile', author.username)
    form = EditProfileForm(request.POST or None, files=request.FILES or None,
                           instance=author)
    if not form.is_valid():
        return render(request, 'posts/edit_profile.html', {'form': form})
    form.save()
    return redirect('posts:profile', author.username)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    author = post.author
    following = request.user.is_authenticated and (Follow.objects.filter(
        user=request.user, author=author).exists())
    context = {
        'post': post,
        'form': form,
        'comments': post.comments.all(),
        'following': following,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=post.author.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    post.delete()
    return redirect('posts:profile', request.user)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_child_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    form = CommentForm(request.POST or None)
    if comment.parent:
        return redirect('posts:post_detail', comment.post.id)
    if not form.is_valid():
        comments = Comment.objects.filter(post_id=comment.post.id)
        context = {
            'post': comment.post,
            'form': form,
            'comments': comments,
            'comment': comment,
        }
        return render(request, 'posts/post_detail.html',
                      context)
    child_comment = form.save(commit=False)
    child_comment.post = comment.post
    child_comment.author = request.user
    child_comment.parent = comment
    child_comment.save()
    return redirect('posts:post_detail', comment.post.id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in [comment.author, comment.post.author]:
        comment.delete()
    return redirect('posts:post_detail', post_id=comment.post.id)


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('posts:post_detail', comment.post.id)
    form = CommentForm(request.POST or None, instance=comment)
    if not form.is_valid():
        comments = Comment.objects.filter(post_id=comment.post.id)
        context = {
            'post': comment.post,
            'form': form,
            'comments': comments,
            'comment': comment,
        }
        return render(request, 'posts/post_detail.html', context)
    form.save()
    return redirect('posts:post_detail', comment.post.id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': get_page_obj(request, posts),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user, author__username=username).delete()
    return redirect('posts:profile', username)


@permission_required(perm='posts.view_group',
                     raise_exception=PermissionError)
def groups_index(request):
    groups = Group.objects.all()
    context = {
        'groups': groups,
    }
    return render(request, 'posts/groups.html', context)


@permission_required(perm='posts.add_group',
                     raise_exception=PermissionError)
def group_create(request):
    form = EditGroupsForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_group.html', {'form': form})
    form.save()
    return redirect('posts:groups_index')


@permission_required(perm='posts.change_group',
                     raise_exception=PermissionError)
def groups_edit(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    form = EditGroupsForm(request.POST or None, instance=group)
    if not form.is_valid():
        return render(request, 'posts/create_group.html', {'form': form})
    form.save()
    return redirect('posts:groups_index')


@permission_required(perm='posts.delete_group',
                     raise_exception=PermissionError)
def groups_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    return redirect('posts:groups_index')
