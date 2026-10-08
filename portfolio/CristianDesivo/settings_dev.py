"""Local development settings: DEBUG on and live browser reload.

Run with:
    python manage.py runserver --settings=CristianDesivo.settings_dev
"""
from .settings import *  # noqa: F401,F403

DEBUG = True

# Serve static files straight from STATICFILES_DIRS instead of the hashed
# manifest, so edits to static files show up without running collectstatic.
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

INSTALLED_APPS = INSTALLED_APPS + ['django_browser_reload']
MIDDLEWARE = MIDDLEWARE + ['django_browser_reload.middleware.BrowserReloadMiddleware']
ROOT_URLCONF = 'CristianDesivo.urls_dev'
