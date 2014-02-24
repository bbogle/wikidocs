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