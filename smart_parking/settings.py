"""
Django settings for smart_parking project.
Generated (and hand‑tuned) July 2025.
"""

from pathlib import Path
import os
from datetime import timedelta   # not used yet, but handy for JWT / sessions

# ──────────────────────────────────────────────────────────────────────────
# CORE PATHS
# ──────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────────────────────
# SECURITY
# ──────────────────────────────────────────────────────────────────────────
# Replace this ASAP for production!
SECRET_KEY = "django-insecure-CHANGE_THIS_TO_YOUR_OWN_48_CHAR_RANDOM_STRING"

DEBUG = True                      # Turn OFF in production!
ALLOWED_HOSTS = []                # e.g. ["yourdomain.com"] in prod

# ──────────────────────────────────────────────────────────────────────────
# APPLICATIONS
# ──────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your custom app
    "parking",
]

# ──────────────────────────────────────────────────────────────────────────
# MIDDLEWARE (order matters)
# ──────────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",      # must be BEFORE Auth
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ──────────────────────────────────────────────────────────────────────────
# URLS & WSGI
# ──────────────────────────────────────────────────────────────────────────
ROOT_URLCONF = "smart_parking.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # If you want global template dirs, add them here:
        "DIRS": [],
        "APP_DIRS": True,                 # crucial for app templates
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "smart_parking.wsgi.application"

# ──────────────────────────────────────────────────────────────────────────
# DATABASE (SQLite for dev; switch to Postgres in prod)
# ──────────────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ──────────────────────────────────────────────────────────────────────────
# PASSWORD VALIDATORS
# ──────────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ──────────────────────────────────────────────────────────────────────────
# INTERNATIONALIZATION
# ──────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"        # adjust if needed
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────────────────────────────────
# STATIC & MEDIA
# ──────────────────────────────────────────────────────────────────────────
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]        # <project>/static/
STATIC_ROOT = BASE_DIR / "staticfiles"          # for collectstatic (prod)

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"                 # user-uploaded files

# ──────────────────────────────────────────────────────────────────────────
# DEFAULT PRIMARY KEY TYPE
# ──────────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"