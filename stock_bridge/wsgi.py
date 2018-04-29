"""
WSGI config for stock_bridge project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
# from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_bridge.settings")

# Cron Jobs
# call_command('runcrons')

application = get_wsgi_application()
