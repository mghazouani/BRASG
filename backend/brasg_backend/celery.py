import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brasg_backend.settings')
app = Celery('brasg_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
