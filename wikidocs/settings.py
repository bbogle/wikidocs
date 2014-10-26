# Django settings for wikidocs project.
import os
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import djcelery
djcelery.setup_loader()

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('YOUR ADMIN NAME', 'YOUR ADMIN EMAIL'),
)

MANAGERS = ADMINS
SEND_BROKEN_LINK_EMAILS = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'wikidocs',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'wikidocs',
        'PASSWORD': 'wikidocs',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}
# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Seoul'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ko-kr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False


STATIC_ROOT = BASE_DIR+'/book/static'
STATIC_URL = '/static/'
MEDIA_ROOT = BASE_DIR+'/upload'
MEDIA_URL = '/images/'


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'YOUR SECRET KEY'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'wikidocs.middleware.minidetector.Middleware',
)

ROOT_URLCONF = 'wikidocs.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wikidocs.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.

    SITE_ROOT+"/templates",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.humanize',
    'django.contrib.sitemaps',

    'south',
    'reversion',
    'reversion_compare',
    'mailer',
    'djcelery',
    'daterange_filter',
    'social_auth',
    'gunicorn',
    'book',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    'social_auth.context_processors.social_auth_by_type_backends',
)


CACHE_USE = True
CACHE_DIR = SITE_ROOT+"/../cache"

# GMAIL
EMAIL_USE_TLS = True
EMAIL_HOST = 'YOUR SMTP HOST'
EMAIL_HOST_USER = 'YOUR SMTP EMAIL'
EMAIL_HOST_PASSWORD = 'YOUR SMTP PASSWORD'
EMAIL_PORT = 587
EMAIL_BACKEND = "mailer.backend.DbBackend"
DEFAULT_FROM_EMAIL = 'YOURE SMTP EMAIL'

# celery & redis
BROKER_URL = 'redis://cache-t2-micro.yzqaxj.0001.apne1.cache.amazonaws.com:6379/0'


# ---------------------------------------------------------------------------
# social auth
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ('google-oauth2', 'facebook')

LOGIN_URL = "/loginForm"
LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL = '/login/auth/error'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/login/auth'
SOCIAL_AUTH_DEFAULT_USERNAME = 'NewUser'
SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True
SOCIAL_AUTH_SESSION_EXPIRATION = False

# facebook
FACEBOOK_APP_ID = 'YOUR FACEBOOK_APP_ID'
FACEBOOK_API_SECRET = 'YOUR FACEBOOK_API_SECRET'
FACEBOOK_EXTENDED_PERMISSIONS = [
    'email',
]

# google oauth2
GOOGLE_OAUTH2_CLIENT_ID = 'YOUR GOOGLE_OAUTH2_CLIENT_ID'
GOOGLE_OAUTH2_CLIENT_SECRET = 'YOUR GOOGLE_OAUTH2_CLIENT_SECRET'

# ---------------------------------------------------------------------------
# caches & redis
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_HOST = 'cache-t2-micro.yzqaxj.0001.apne1.cache.amazonaws.com'
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 5

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'cache-t2-micro.yzqaxj.0001.apne1.cache.amazonaws.com:6379',
        'OPTIONS': {
            'DB': 6,
        },
        'TIMEOUT':9999999,
    },
}
CACHE_TIMEOUT = 0

if os.environ.get('DEVELOPMENT', None):
    from settings_dev import *

try:
    from secret_key import *
except ImportError:
    print "Please see README.md"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR+'/logs/django_error.log',
        },

        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
