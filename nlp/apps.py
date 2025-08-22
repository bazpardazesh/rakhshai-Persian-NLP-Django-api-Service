"""
Application configuration for the ``nlp`` app.

This class provides metadata to Django about the ``nlp`` application. The
``default_auto_field`` attribute ensures that model primary keys use a 64‑bit
integer by default.
"""

from django.apps import AppConfig


class NlpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nlp'
    verbose_name = 'Persian NLP Service'