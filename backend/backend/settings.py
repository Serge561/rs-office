# pylint: disable=line-too-long, import-error
"""
Django settings for backend project.

"""

import os
from pathlib import Path
from celery.schedules import crontab
from decouple import Config, RepositoryEnv, Csv
from django.contrib.messages import constants as messages
import pycountry

# config = Config(RepositoryEnv("docker/env/.env.dev"))
config = Config(RepositoryEnv("docker/env/.env.prod"))

MESSAGE_TAGS = {
    messages.DEBUG: "h-14 font-regular relative block w-full rounded-b-lg bg-blue-200 p-4 text-base leading-5 text-pink-600 opacity-100",  # noqa: E501
    messages.INFO: "h-14 font-regular relative block w-full rounded-b-lg bg-blue-200 p-4 text-base leading-5 text-blue-800 opacity-100",  # noqa: E501
    messages.SUCCESS: "h-14 font-regular relative block w-full rounded-b-lg bg-green-200 p-4 text-base leading-5 text-green-800 opacity-100",  # noqa: E501
    messages.WARNING: "h-14 font-regular relative block w-full rounded-b-lg bg-red-100 p-4 text-base leading-5 text-red-500 opacity-100",  # noqa: E501
    messages.ERROR: "h-14 font-regular relative block w-full rounded-b-lg bg-red-200 p-4 text-base leading-5 text-red-800 opacity-100",  # noqa: E501
}

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1", cast=Csv())

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS", default="http://127.0.0.1", cast=Csv()
)

# Application definition

INSTALLED_APPS = [
    "dal",
    "dal_select2",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "modules.companies.apps.CompaniesConfig",
    "modules.system.apps.SystemConfig",
    "modules.applications.apps.ApplicationsConfig",
    "modules.services",
    "tailwind",
    "theme",
    "django_browser_reload",
    "debug_toolbar",
    "phonenumber_field",
    "localflavor",
]

TAILWIND_APP_NAME = "theme"

INTERNAL_IPS = [
    "127.0.0.1",
]

SITE_ID = 1

NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "modules.system.middleware.ActiveUserMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": config("POSTGRES_PORT", cast=int),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa: E501
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/


LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Kaliningrad"

USE_TZ = True

USE_I18N = True

USE_L10N = False

DATE_FORMAT = "E"

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
    pycountry.LOCALES_DIR,
)


def ugettext(s):
    "klklk"
    return s


LANGUAGES = (
    ("en", ugettext("English")),
    ("ru", ugettext("Russin")),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
# STATIC_URL = '/static/'

# if not DEBUG:
#    STATIC_ROOT = '/home/django/www-data/example.com/static/'

# STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, 'static/'),
# ]

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "/static/")

# STATICFILES_DIRS = (os.path.join(BASE_DIR, "static", "/theme/static/"),)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static/"),
]

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "system.User"

LOGOUT_REDIRECT_URL = "home"

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Email configuration
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=25, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_SERVER = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = config("EMAIL_ADMIN", default="localhost")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_LOCATION"),
    }
}

# Celery settings
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="")
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Kaliningrad"

CELERY_BEAT_SCHEDULE = {
    "backup_database": {
        "task": "modules.services.tasks.dbackup_task",  # Путь к задаче указанной в tasks.py  # noqa: E501
        "schedule": crontab(
            hour=0, minute=0  # type: ignore
        ),  # Резервная копия будет создаваться каждый день в полночь
    },
}
