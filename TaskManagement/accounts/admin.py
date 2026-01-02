from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Role, UserProfile

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_code', 'name', 'level', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('role_code', 'name')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'manager')
    list_filter = ('role',)
    search_fields = ('user__username', 'manager__username')
    autocomplete_fields = ('user', 'manager')


