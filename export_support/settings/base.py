"""
Django settings for export_support project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import string
from pathlib import Path

import environ

environ.Env.read_env(".env")  # reads the .env file
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

ENABLE_CSP = env.bool("ENABLE_CSP", True)

# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "export_support.core",
    "export_support.gds",
    "export_support.cookies",
    "webpack_loader",
    "csp",
    "formtools",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "export_support.core.middleware.no_index_middleware",
    "export_support.core.middleware.no_cache_middleware",
]

if ENABLE_CSP:
    MIDDLEWARE += ["csp.middleware.CSPMiddleware"]

BASIC_AUTH = env.dict("BASIC_AUTH", default=None)
if BASIC_AUTH:
    MIDDLEWARE += ["basicauth.middleware.BasicAuthMiddleware"]
    BASICAUTH_USERS = BASIC_AUTH

ROOT_URLCONF = "export_support.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "export_support.core.context_processors.external_urls",
                "export_support.core.context_processors.current_path",
            ],
        },
    },
]

WSGI_APPLICATION = "export_support.wsgi.application"

VCAP_SERVICES = env.json("VCAP_SERVICES", {})

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {}

if "redis" in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES["redis"][0]["credentials"]["uri"]
else:
    REDIS_URL = env.str("REDIS_URL")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "build/assets")]
STATIC_ROOT = "build/static"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

GOV_UK_EXPORT_GOODS_URL = "https://www.gov.uk/export-goods"
GREAT_OFFICE_FINDER_URL = "https://www.great.gov.uk/contact/office-finder/"

if ENABLE_CSP:
    CSP_DEFAULT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = ("'self'",)
    CSP_SCRIPT_SRC_ELEM = ("'self'",)
    CSP_STYLE_SRC_ATTR = ("'self'",)
    CSP_INCLUDE_NONCE_IN = ("script-src-elem",)

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = "Strict"

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_AGE = 31 * 24 * 60 * 60

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

GTM_AUTH = env.str("GTM_AUTH", None)
GTM_ID = env.str("GTM_ID", None)

REFERENCE_NUMBER_ALPHABET = string.ascii_uppercase + string.digits
REFERENCE_NUMBER_SIZE = 8
