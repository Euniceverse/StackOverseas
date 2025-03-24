"""
Django settings for uni_society project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from django.contrib.messages import constants as messages
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@h)j0-+ym+l*&l)r_qyca^#z3vr-@jawo!sna2^+(u9uy!jfwy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'overseasstack@gmail.com'
EMAIL_HOST_PASSWORD = 'btlmfvczvkrffiiy'
EMAIL_USE_TLS = True
PASSWORD_RESET_TIMEOUT = 14400 # 4 hours

# Strip Payment
#STRIPE_PUBLIC_KEY = "pk_test_51QviGhCivs73HAIb0tIGL6u609Zb1ugKLnKhX2KAWXGHNbhod64MBQZLI0aXiihufN0w1XjdFW3JjjyM9TEoEYVx00NaRxAXxk" 
STRIPE_PUBLIC_KEY = "pk_test_51QviGaE1rp8ABg2BZkClndNES4HcFS2yJVKbc10uIfMf9jF6QuuS1TKZ7SgVKU8DK43TXWzQlS1fGcswox4WFuve00bNqjsbvD"
STRIPE_SECRET_KEY = "sk_test_51QviGaE1rp8ABg2B5FjMH41ur4Ud9tVa7ehaWILwhobjmC4SBjWPTYm9a7DDmBPZVMRus3AzzARkpymzj4h2zsWw00Hg0K7rJI"

DOMAIN_NAME = "http://127.0.0.1:8000"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'widget_tweaks',
    'rest_framework',
    'django_filters',


    'apps.events',
    'apps.news',
    'apps.societies',
    'apps.users',
    'apps.payments'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "config" / "templates"],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Media Files
MEDIA_URL = 'media/'

MEDIA_ROOT = BASE_DIR / 'config' / 'media'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('SQLITE_DB_PATH',  '/mnt/data/db.sqlite3'), # for home computer: BASE_DIR / 'db.sqlite3', for render: '/mnt/data/db.sqlite3'
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "config" / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# User model for authentication and login purposes
AUTH_USER_MODEL = 'users.CustomUser'

# Login URL for redirecting users from login protected views
LOGIN_URL = 'log_in'

# URL where @login_prohibited redirects to
REDIRECT_URL_WHEN_LOGGED_IN = 'home'

# Convert Django ERROR messages to Bootstrap DANGER messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}







# Add this after INSTALLED_APPS
SITE_ID = 1

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}




ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    "stackoverseas.onrender.com",
    os.getenv("RENDER_EXTERNAL_HOSTNAME", ""),
]

DOMAIN_NAME = "127.0.0.1:8000"  # Change this if running on another port

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "https://checkout.stripe.com",
]