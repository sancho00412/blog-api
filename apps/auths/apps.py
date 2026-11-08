# Django modules
from django.apps import AppConfig


class AuthsConfig(AppConfig):
    """Config for the auths app: custom user model and JWT authentication."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auths"
    label = "auths"
