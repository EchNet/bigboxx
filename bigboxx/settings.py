"""
Canonical settings for the project.
"""
import os
import sys

import raven
import datetime as datetime
from celery.schedules import crontab
from decouple import config
from dj_database_url import parse as db_url

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_ROOT = os.path.join(SITE_ROOT, "apps")
sys.path.insert(0, APPS_ROOT)

# Environment
DEBUG = config("DEBUG", cast=bool)
STAGING = config("STAGING", cast=bool)
DEMO = config("DEMO", cast=bool)
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"
SECRET_KEY = config("SECRET_KEY")
SITE_URL = config("SITE_URL")
ENV = config("ENV")
ENV_COLOR = config("ENV_COLOR")
ALLOWED_HOSTS = ["*"]  # TODO: Change to allowed domains

DATA_UPLOAD_MAX_MEMORY_SIZE = 512 * 1024  # Uploads go directly to S3.  This limit can be low.

USE_X_FORWARDED_PORT = True

# Application definition
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # 3rd party
    "django_extensions",
    "django_object_actions",
    "djcelery_email",
    "gunicorn",
    "localflavor",
    "phonenumber_field",
    "raven.contrib.django.raven_compat",
    "storages",
    "widget_tweaks",
    "corsheaders",
    "rest_framework",
    "rest_framework_swagger",
    'import_export',

    # custom apps
    "api",
    "utils")

MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    "utils.middleware.MySslMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # to serve static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

ROOT_URLCONF = "bigboxx.urls"
WSGI_APPLICATION = "bigboxx.wsgi.application"

# Caching
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Database
DATABASES = {"default": config("DATABASE_URL", cast=db_url)}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = 60

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": ("django.contrib.auth.password_validation"
                 ".UserAttributeSimilarityValidator")
    },
    {
        "NAME": ("django.contrib.auth.password_validation"
                 ".MinimumLengthValidator")
    },
    {
        "NAME": ("django.contrib.auth.password_validation"
                 ".CommonPasswordValidator")
    },
    {
        "NAME": ("django.contrib.auth.password_validation"
                 ".NumericPasswordValidator")
    },
]

# Password reset parameters, also apply to invitations.
PASSWORD_RESET_TIMEOUT_DAYS = 5

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        # Send all messages to console
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        # This is the "catch all" logger
        "": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": True,
            "filters": ["require_debug_true"]
        },
    }
}

# SSL
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", cast=bool, default=True)

# Static file
SERVE_MEDIA = DEBUG
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(SITE_ROOT, "media")

STATIC_DEV = os.path.join(SITE_ROOT, "static_dev")
STATICFILES_DIRS = (STATIC_DEV, )
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
STATIC_ROOT = os.path.join(SITE_ROOT, "static")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_URL = "/static/"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(SITE_ROOT, "templates"),
            os.path.join(SITE_ROOT, "build"),
        ],
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

# celery
CELERY_ACCEPT_CONTENT = ["application/x-python-serialize", "application/json"]
CELERY_BROKER_URL = config("REDIS_URL")
CELERY_REDIS_MAX_CONNECTIONS = 4
CELERY_RESULT_BACKEND = config("REDIS_URL")
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_RESULT_EXPIRES = 60 * 60  # seconds
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_WORKER_CONCURRENCY = 2

CELERY_BEAT_SCHEDULER = "redbeat.RedBeatScheduler"
CELERY_BEAT_SCHEDULE = {
    "celery.backend_cleanup": {
        "task": "celery.backend_cleanup",
        "schedule": crontab(minute="0", hour="*"),  # every hour
        "options": {
            "expires": 30 * 60  # seconds
        }
    },
}

# phonenumber_field
PHONENUMBER_DEFAULT_REGION = "US"

# raven/sentry
RAVEN_DSN = config("RAVEN_DSN", default=None)
try:
  release = raven.fetch_git_sha(SITE_ROOT)
except Exception:
  # TODO: Fix this
  release = None
if RAVEN_DSN:
  RAVEN_CONFIG = {
      "dsn": RAVEN_DSN,
      # "release": raven.fetch_git_sha(SITE_ROOT),
  }
  if release:
    RAVEN_CONFIG["release"] = release

# storages
DEFAULT_FILE_STORAGE = config("DEFAULT_FILE_STORAGE")
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default=None)
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default=None)
AWS_DOWNLOAD_BUCKET_NAME = config("AWS_DOWNLOAD_BUCKET_NAME", default=None)
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "private"

# rest_framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated', ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

# JWT
JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300),
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}
