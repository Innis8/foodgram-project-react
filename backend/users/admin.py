from django.contrib import admin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'username', 'first_name', 'last_name', 'is_superuser',
    )
    search_fields = ('username', 'first_name', 'email',)
    list_filter = ('username', 'first_name', 'email',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'user',)
    search_fields = ('id', 'author', 'user',)
    list_filter = ('user', 'author',)
