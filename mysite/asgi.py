"""
ASGI config for the Persian NLP service.

This module exposes the ASGI application used by Django's development server
and any production ASGI deployments. It loads the settings module and
provides an application callable named ``application``.

For more information, see:
https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

application = get_asgi_application()