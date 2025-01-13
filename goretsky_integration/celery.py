import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goretsky_integration.settings')

app = Celery('goretsky_integration')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
