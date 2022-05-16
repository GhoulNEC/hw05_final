from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/edit/', views.edit_profile,
         name='edit_profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('posts/<int:post_id>/comment/', views.add_comment,
         name='add_comment'),
    path('posts/comment/<int:comment_id>/reply/', views.add_child_comment,
         name='add_child_comment'),
    path('posts/comment/<int:comment_id>/delete/', views.delete_comment,
         name='delete_comment'),
    path('posts/comment/<int:comment_id>/edit/', views.edit_comment,
         name='edit_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path('profile/<str:username>/follow/', views.profile_follow,
         name='profile_follow'),
    path('profile/<str:username>/unfollow', views.profile_unfollow,
         name='profile_unfollow'),
    path('moderator/groups/', views.groups_index, name='groups_index'),
    path('moderator/group_create/', views.group_create, name='group_create'),
    path('moderator/<int:group_id>/edit/', views.groups_edit,
         name='group_edit'),
    path('moderator/<int:group_id>/delete/', views.groups_delete,
         name='group_delete'),
]
