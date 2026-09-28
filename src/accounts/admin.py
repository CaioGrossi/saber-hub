from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('SaberHub', {'fields': ('role', 'college')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('SaberHub', {'fields': ('role', 'college')}),
    )
    list_display = ('username', 'role', 'college', 'is_staff')
