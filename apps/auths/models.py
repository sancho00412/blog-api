# Django modules
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import BooleanField, CharField, DateTimeField, EmailField
from django.utils import timezone

# Project modules
from apps.auths.constants import FIRST_NAME_MAX_LENGTH, LAST_NAME_MAX_LENGTH
from apps.auths.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user. Logs in with email instead of username."""

    email = EmailField(unique=True)
    first_name = CharField(max_length=FIRST_NAME_MAX_LENGTH)
    last_name = CharField(max_length=LAST_NAME_MAX_LENGTH)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    date_joined = DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ("-date_joined",)

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        """Return first name and last name with a space between."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self) -> str:
        """Return the first name."""
        return self.first_name
