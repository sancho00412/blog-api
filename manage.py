#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

# Python modules
import os
import sys

# Project modules
from settings.conf import ENV_ID

ALLOWED_ENV_IDS: tuple[str, ...] = ("local", "prod")
SETTINGS_MODULE_TEMPLATE: str = "settings.env.{env_id}"


def main() -> None:
    """Pick the settings module from BLOG_ENV_ID and run the command."""
    if ENV_ID not in ALLOWED_ENV_IDS:
        raise RuntimeError(
            f"BLOG_ENV_ID must be one of {ALLOWED_ENV_IDS}, got '{ENV_ID}'. "
            "Check settings/.env."
        )

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        SETTINGS_MODULE_TEMPLATE.format(env_id=ENV_ID),
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
