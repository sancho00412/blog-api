"""Production settings."""

# Project modules
from settings.base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS: list[str] = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": POSTGRES_DB,  # noqa: F405
        "USER": POSTGRES_USER,  # noqa: F405
        "PASSWORD": POSTGRES_PASSWORD,  # noqa: F405
        "HOST": POSTGRES_HOST,  # noqa: F405
        "PORT": POSTGRES_PORT,  # noqa: F405
    },
}
