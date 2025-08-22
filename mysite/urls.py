"""
URL configuration for the Persian NLP service.

The ``urlpatterns`` list routes URLs to views. For more information, please
see: https://docs.djangoproject.com/en/stable/topics/http/urls/

Each view is represented either as a callable or as a class-based view. This
module connects the API endpoints under the ``/api/`` prefix to the
application defined in ``nlp/urls.py``.
"""

from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # Admin site (optional). Remove or secure in production.
    path('admin/', admin.site.urls),
    # API routes for NLP analysis
    path('api/', include('nlp.urls')),
]