# Django modules
from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Config for the blog app: posts, comments, categories, tags."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.blog"
    label = "blog"
