from pathlib import Path
import os
from datetime import timedelta

# This is necessary for Django to use pymysql with your MySQL database.
import pymysql
pymysql.install_as_MySQLdb()

# ──────────────────────────────────────────────────────────────────────────
# CORE PATHS
# ──────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────────────────────
# SECURITY
# ──────────────────────────────────────────────────────────────────────────
SECRET_KEY = "django-insecure-CHANGE_THIS_TO_YOUR_OWN_48_CHAR_RANDOM_STRING"

# DEBUG should be True for development and False for production.
DEBUG = True

# Allow all hosts for local development. For production, list your domain(s).
ALLOWED_HOSTS = ['*']

# ──────────────────────────────────────────────────────────────────────────
# APPLICATIONS
# ──────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",  # <-- THIS IS THE FIX
    # Local Apps
    "parking",
    # Third-Party Apps
    'background_task',
]

# ──────────────────────────────────────────────────────────────────────────
# MIDDLEWARE (order matters)
# ──────────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
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
        "DIRS": [BASE_DIR / "templates"], # For project-level templates
        "APP_DIRS": True,
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
# DATABASE (MySQL)
# ──────────────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smart_parking_db',
        'USER': 'root',
        'PASSWORD': 'root', # Replace with your MySQL password if you have one
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# ──────────────────────────────────────────────────────────────────────────
# PASSWORD VALIDATORS
# ──────────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ──────────────────────────────────────────────────────────────────────────
# AUTHENTICATION
# ──────────────────────────────────────────────────────────────────────────
# Use namespaced URLs to avoid conflicts
LOGIN_URL = 'parking:login_view'
LOGIN_REDIRECT_URL = 'parking:home'
LOGOUT_REDIRECT_URL = 'parking:login_view'

# ──────────────────────────────────────────────────────────────────────────
# INTERNATIONALIZATION
# ──────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────────────────────────────────
# STATIC & MEDIA FILES
# ──────────────────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles" # For production deployment

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ──────────────────────────────────────────────────────────────────────────
# EMAIL CONFIGURATION (for Gmail)
# ──────────────────────────────────────────────────────────────────────────
# You MUST generate a 16-digit "App Password" from your Google Account.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'hunterparama@gmail.com'
EMAIL_HOST_PASSWORD = 'fzyfvturnwebjxke' # This is your App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ──────────────────────────────────────────────────────────────────────────
# DEFAULT PRIMARY KEY TYPE
# ──────────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
