from django.contrib import admin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'username', 'first_name', 'last_name', 'is_superuser',
    )
    search_fields = (
        'email', 'username', 'first_name', 'last_name', 'is_superuser',
    )
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user',)
    search_fields = ('author', 'user',)
