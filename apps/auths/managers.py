# Python modules
from typing import TYPE_CHECKING, Any

# Django modules
from django.contrib.auth.models import BaseUserManager

# Project modules
from apps.auths.constants import (
    EMAIL_REQUIRED_MESSAGE,
    FIRST_NAME_REQUIRED_MESSAGE,
    LAST_NAME_REQUIRED_MESSAGE,
    SUPERUSER_STAFF_MESSAGE,
    SUPERUSER_SUPERUSER_MESSAGE,
)

if TYPE_CHECKING:
    from apps.auths.models import User


class UserManager(BaseUserManager["User"]):
    """Manager for the custom User model. Login field is email."""

    use_in_migrations = True

    def normalize_email(self, email: str | None) -> str:
        """Return the email in lowercase without spaces around it."""
        return (email or "").strip().lower()

    def _create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        password: str | None,
        **extra_fields: Any,
    ) -> "User":
        """Check required fields, hash the password and save the user."""
        if not email:
            raise ValueError(EMAIL_REQUIRED_MESSAGE)
        if not first_name:
            raise ValueError(FIRST_NAME_REQUIRED_MESSAGE)
        if not last_name:
            raise ValueError(LAST_NAME_REQUIRED_MESSAGE)

        user: User = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        user.set_password(password)  # hashes the password
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        """Create a regular user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, first_name, last_name, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        first_name: str,
        last_name: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        """Create a superuser. Used by `manage.py createsuperuser`."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(SUPERUSER_STAFF_MESSAGE)
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(SUPERUSER_SUPERUSER_MESSAGE)

        return self._create_user(email, first_name, last_name, password, **extra_fields)
