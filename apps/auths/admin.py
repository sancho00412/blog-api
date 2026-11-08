# Django modules
from django.contrib import admin

# Project modules
from apps.auths.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Basic admin for User. It will be redesigned with Unfold in HW2."""

    list_display = ("email", "first_name", "last_name", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("last_login", "date_joined")
