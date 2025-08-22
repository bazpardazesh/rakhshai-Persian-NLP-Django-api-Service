"""
Celery configuration for the Persian NLP service.

This module creates a Celery application that integrates with Django. It
reads configuration from Django's settings and autodiscovers tasks defined
in any installed application. Celery is optional—if you do not wish to use
asynchronous tasks for processing large files, you may omit running the
Celery worker and remove the ``nlp/tasks.py`` file.
"""

from __future__ import annotations
import os
from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')

# Using a string here means the worker will not have to pickle the object
# when using Windows. Adjust the namespace if you change Celery-related
# settings keys.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self) -> None:
    """A simple debugging task that prints the request details."""
    print(f'Request: {self.request!r}')