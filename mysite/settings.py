"""
Django settings for the Persian NLP service.

This settings module configures the Django project for development. It uses
SQLite as the default database and includes Django REST Framework and the
custom ``nlp`` application for Persian text analysis. If Celery is
available, its configuration is provided at the bottom of this file. For
deployment or production use, adjust the settings accordingly (e.g., use
a stronger secret key, configure allowed hosts, and switch to a production
database).

**Copyright**: All rights to this project belong to ``rakhshai``. The
software is released as a beta version for demonstration and educational
purposes.
"""

from pathlib import Path


# -----------------------------------------------------------------------------
# Base directory of the project
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------
# WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-CHANGE_ME_SECRET_KEY'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow all hosts during development. Update this list in production.
ALLOWED_HOSTS: list[str] = []


# -----------------------------------------------------------------------------
# Application definition
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third‑party apps
    'rest_framework',
    # Local apps
    'nlp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
# Use SQLite for development. For production use, choose another database
# backend and provide appropriate credentials.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# -----------------------------------------------------------------------------
# Password validation
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# -----------------------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------------------
# Using Persian locale but English fallback for code-level messages. Adjust
# LANGUAGE_CODE to 'fa' if you want full Persian translation support.
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# -----------------------------------------------------------------------------
# Static files
# -----------------------------------------------------------------------------
# URL prefix for static files and directory where collected files will be stored.
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# -----------------------------------------------------------------------------
# Default primary key field type
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -----------------------------------------------------------------------------
# Celery configuration
# -----------------------------------------------------------------------------
# These settings configure Celery to use Redis as both the message broker and
# result backend. Ensure that a Redis server is running at the specified
# address if you plan to process long‑running tasks (e.g., analysing large
# text files). If you prefer synchronous execution or do not want to run
# Celery at all, you can remove these entries and delete the tasks module.

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'


# -----------------------------------------------------------------------------
# Version and copyright
# -----------------------------------------------------------------------------
# Provide explicit version information. This constant can be imported from
# elsewhere in the project if needed (e.g., to expose via an API endpoint).
VERSION = '0.1-beta'

COPYRIGHT_OWNER = 'rakhshai'
