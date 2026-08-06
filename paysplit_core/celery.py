# paysplit_core/celery.py
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paysplit_core.settings')

app = Celery('paysplit_core')

# Read config from Django settings, using a 'CELERY_' prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks in all registered apps
app.autodiscover_tasks()