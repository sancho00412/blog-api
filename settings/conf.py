"""Read settings/.env and export config variables.

All environment variables use the BLOG_ prefix.
"""

# Python modules
from pathlib import Path

# Third party modules
from decouple import AutoConfig

SETTINGS_DIR: Path = Path(__file__).resolve().parent

config = AutoConfig(search_path=SETTINGS_DIR)

# ----------------------------------------------
# General
#
ENV_ID: str = config("BLOG_ENV_ID", cast=str)
SECRET_KEY: str = config("BLOG_SECRET_KEY", cast=str)

# ----------------------------------------------
# PostgreSQL (used only in prod)
#
POSTGRES_DB: str = config("BLOG_POSTGRES_DB", cast=str, default="")
POSTGRES_USER: str = config("BLOG_POSTGRES_USER", cast=str, default="")
POSTGRES_PASSWORD: str = config("BLOG_POSTGRES_PASSWORD", cast=str, default="")
POSTGRES_HOST: str = config("BLOG_POSTGRES_HOST", cast=str, default="localhost")
POSTGRES_PORT: int = config("BLOG_POSTGRES_PORT", cast=int, default=5432)
