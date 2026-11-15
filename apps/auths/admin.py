from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.decorators import action, display
from unfold.forms import AdminPasswordChangeForm

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from apps.auths.forms import UserChangeForm, UserCreationForm
from apps.auths.models import User

TAB: list[str] = ["tab"]


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ["user_header", "active_label", "staff_label", "posts_count"]
    list_filter = [("is_active", BooleanRadioFilter), ("is_staff", BooleanRadioFilter)]
    list_filter_submit = True
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]
    actions = ["activate", "deactivate"]
    readonly_fields = ["last_login", "date_joined"]

    fieldsets = [
        (
            "Personal info",
            {"classes": TAB, "fields": ["email", "password", "first_name", "last_name"]},
        ),
        (
            "Permissions",
            {"classes": TAB, "fields": ["is_active", "is_staff", "is_superuser", "groups"]},
        ),
        ("Important dates", {"classes": TAB, "fields": ["last_login", "date_joined"]}),
    ]
    add_fieldsets = [
        (None, {"fields": ["email", "first_name", "last_name", "password1", "password2"]}),
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(posts_total=Count("posts"))

    @display(description="User", header=True)
    def user_header(self, obj: User) -> list[str]:
        initials: str = obj.first_name[:1] + obj.last_name[:1]
        return [obj.get_full_name(), obj.email, initials]

    @display(description="Active", label={True: "success", False: "danger"})
    def active_label(self, obj: User) -> tuple[bool, str]:
        return obj.is_active, "Active" if obj.is_active else "Inactive"

    @display(description="Staff", label={True: "info", False: "warning"})
    def staff_label(self, obj: User) -> tuple[bool, str]:
        return obj.is_staff, "Staff" if obj.is_staff else "User"

    @display(description="Posts", ordering="posts_total")
    def posts_count(self, obj: User) -> int:
        return obj.posts_total

    @action(description="Activate selected users")
    def activate(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_active=True)

    @action(description="Deactivate selected users")
    def deactivate(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_active=False)


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
