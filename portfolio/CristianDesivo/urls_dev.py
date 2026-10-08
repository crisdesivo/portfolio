"""Development URLs: the normal site plus django-browser-reload's endpoint."""
from django.urls import include, path

from .urls import urlpatterns as base_urlpatterns

# Must come first: MEDIA_URL is '/', so the media pattern in urls.py matches
# every path and would swallow anything listed after it.
urlpatterns = [
    path('__reload__/', include('django_browser_reload.urls')),
] + base_urlpatterns
