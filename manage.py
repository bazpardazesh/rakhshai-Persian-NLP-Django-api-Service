#!/usr/bin/env python3
"""
Manage script for the Django project. This file provides the command-line
interface for administrative tasks such as running the development server or
executing database migrations. It sets up the Django environment and then
delegates to Django's management utility.

This project is released under a beta version and the copyright belongs to
``rakhshai``. All rights reserved.
"""
import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()