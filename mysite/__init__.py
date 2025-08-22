"""
mysite package initializer.

This file makes Python treat the ``mysite`` directory as a package. It also
exposes the Celery application instance when Celery is used. See
``mysite/celery.py`` for details.
"""

from .celery import app as celery_app

__all__ = ("celery_app",)