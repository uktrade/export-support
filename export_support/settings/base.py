"""
Django settings for export_support project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import sys
from pathlib import Path

import environ
import sentry_sdk
from django_log_formatter_ecs import ECSFormatter
from sentry_sdk.integrations.django import DjangoIntegration

environ.Env.read_env(".env")  # reads the .env file
env = environ.Env()

SENTRY_DSN = env.str("SENTRY_DSN", None)
SENTRY_ENVIRONMENT = env.str("SENTRY_ENVIRONMENT")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        integrations=[DjangoIntegration()],
    )

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
    "export_support.healthcheck",
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
    "django_ga_measurement_protocol.middleware.page_view_tracking_middleware",
    "export_support.core.middleware.no_index_middleware",
    "export_support.core.middleware.no_cache_middleware",
    "export_support.healthcheck.middleware.HealthCheckMiddleware",
]

if ENABLE_CSP:
    MIDDLEWARE += ["csp.middleware.CSPMiddleware"]

BASIC_AUTH = env.dict("BASIC_AUTH", default=None)
if BASIC_AUTH:
    MIDDLEWARE += ["basicauth.middleware.BasicAuthMiddleware"]
    BASICAUTH_USERS = BASIC_AUTH

ROOT_URLCONF = "export_support.urls"

USE_ECS_LOGGING = env.bool("USE_ECS_LOGGING", True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "ecs_formatter": {
            "()": ECSFormatter,
        },
        "console_formatter": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "ecs": {
            "class": "logging.StreamHandler",
            "formatter": "ecs_formatter",
            "stream": sys.stdout,
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console_formatter",
        },
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["ecs" if USE_ECS_LOGGING else "console"],
        },
        "django": {
            "level": "INFO",
            "handlers": ["ecs" if USE_ECS_LOGGING else "console"],
        },
    },
}

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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "exportsupporttempdatabase",
    }
}

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
    _GOOGLE_DOMAINS = (
        "www.googletagmanager.com",
        "*.google-analytics.com",
        "stats.g.doubleclick.net",
        "www.google.com",
        "www.google.co.uk",
    )
    _SENTRY_DOMAINS = ("raven.ci.uktrade.io",)

    CSP_DEFAULT_SRC = ("'self'", *_GOOGLE_DOMAINS, *_SENTRY_DOMAINS)
    csp_script_src_additions = env.tuple("CSP_SCRIPT_SRC_ADDITIONS", default=tuple())
    CSP_SCRIPT_SRC = (
        "'self'",
        "'unsafe-eval'",
        *_GOOGLE_DOMAINS,
        *csp_script_src_additions,
        *_SENTRY_DOMAINS,
    )
    csp_script_src_elem_additions = env.tuple(
        "CSP_SCRIPT_SRC_ELEM_ADDITIONS", default=tuple()
    )
    CSP_SCRIPT_SRC_ELEM = (
        "'self'",
        *_GOOGLE_DOMAINS,
        *csp_script_src_elem_additions,
        *_SENTRY_DOMAINS,
    )
    CSP_STYLE_SRC_ATTR = ("'self'",)
    CSP_INCLUDE_NONCE_IN = (
        "script-src",
        "script-src-elem",
    )
    CSP_REPORT_URI = env.str("CSP_REPORT_URI")

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = "Strict"

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_AGE = 31 * 24 * 60 * 60

ENABLE_SECURE_COOKIES = env.bool("ENABLE_SECURE_COOKIES", True)
if ENABLE_SECURE_COOKIES:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", True)

GTM_ID = env.str("GTM_ID", None)
GTM_AUTH = env.str("GTM_AUTH", None)
GTM_PREVIEW = env.str("GTM_PREVIEW", None)
GTM_COOKIES_WIN = env.str("GTM_COOKIES_WIN", None)

FORM_URL = env.str("FORM_URL")

DIRECTORY_FORMS_API_BASE_URL = env.str("DIRECTORY_FORMS_API_BASE_URL")
DIRECTORY_FORMS_API_API_KEY = env.str("DIRECTORY_FORMS_API_API_KEY")
DIRECTORY_FORMS_API_SENDER_ID = env.str("DIRECTORY_FORMS_API_SENDER_ID")
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = 10
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = env.int(
    "DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS"
)
DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS = env.int(
    "DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS"
)
DIRECTORY_FORMS_API_HEALTHCHECK_URL = env.str("DIRECTORY_FORMS_API_HEALTHCHECK_URL")

ZENDESK_SERVICE_NAME = env.str("ZENDESK_SERVICE_NAME")
ZENDESK_SUBDOMAIN = env.str("ZENDESK_SUBDOMAIN")
ZENDESK_CUSTOM_FIELD_MAPPING = env.dict("ZENDESK_CUSTOM_FIELD_MAPPING", default=dict())

GA_MEASUREMENT_PROTOCOL_UA = env.str("GA_MEASUREMENT_PROTOCOL_UA")
GA_MEASUREMENT_PROTOCOL_TRACK_EVENTS = env.str(
    "GA_MEASUREMENT_PROTOCOL_TRACK_EVENTS", False
)

COMPANIES_HOUSE_TOKEN = env.str("COMPANIES_HOUSE_TOKEN")
