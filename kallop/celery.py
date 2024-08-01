import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kallop.settings')

# Create a Celery application
app = Celery('myproject')

# Load the Celery configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks in all registered Django applications
app.autodiscover_tasks()