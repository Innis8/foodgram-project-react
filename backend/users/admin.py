from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    # list_filter = ('user', 'author',)
    search_fields = ('user__username', 'user__email',)
