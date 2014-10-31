DEBUG = True
CACHE_USE = False

GOOGLE_OAUTH2_CLIENT_ID = '252458061349-nn1f89kt3pldhmutq1j66qbfpv0ifeeb.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET = 'YGvbXUqHZzqbboZ1Zxd1EBli'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}
CACHE_TIMEOUT = 300

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sitemaps',

    'reversion',
    'mailer',
    'djcelery',
    'daterange_filter',
    'social_auth',
    'book',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'wikidocs.test.db',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'wikidocs',
        'PASSWORD': 'wikidocs',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

REAL=False