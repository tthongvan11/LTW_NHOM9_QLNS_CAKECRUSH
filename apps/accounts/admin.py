"""Expose the project's user model in Django Admin."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Vai trò Cake Crush", {"fields": ("role",)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Vai trò Cake Crush", {"fields": ("role",)}),
    )
    list_display = DjangoUserAdmin.list_display + ("role",)
    list_filter = DjangoUserAdmin.list_filter + ("role",)
