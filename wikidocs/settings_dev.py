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
    'book',
)