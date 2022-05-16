from django.contrib import admin

from . import models

from mptt.admin import MPTTModelAdmin


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'description',
        'slug'
    )
    search_fields = ('title',)
    list_filter = ('title',)
    prepopulated_fields = {'slug': ('title',)}


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'user')


class UserAdmin(admin.ModelAdmin):
    list_display = ('permission', 'username', 'first_name',
                    'last_name', 'email', 'birth_date', 'city')
    search_fields = ('username',)


admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Follow, FollowAdmin)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Comment, MPTTModelAdmin)
