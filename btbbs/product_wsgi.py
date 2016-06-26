"""
WSGI config for btbbs project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# python manage.py createsuperuser --settings btbbs.product
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btbbs.product")

application = get_wsgi_application()