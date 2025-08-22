"""
WSGI config for the Persian NLP service.

This module provides the WSGI callable used by Django's runserver and WSGI
servers such as Gunicorn or mod_wsgi. It sets the default settings module
for the project and then creates the application object.

For more information, see:
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

application = get_wsgi_application()