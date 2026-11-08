"""ASGI config for the blog-api project."""

# Python modules
import os

# Django modules
from django.core.asgi import get_asgi_application
from django.core.handlers.asgi import ASGIHandler

# Project modules
from settings.conf import ENV_ID

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{ENV_ID}")

application: ASGIHandler = get_asgi_application()
