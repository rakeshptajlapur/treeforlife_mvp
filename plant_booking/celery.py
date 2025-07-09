import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_booking.settings')

app = Celery('plant_booking')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()