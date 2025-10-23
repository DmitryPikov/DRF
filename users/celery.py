from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.timezone = 'UTC'
app.conf.enable_utc = False

app.conf.beat_schedule = {
    'check-inactive-users': {
        'task': 'users.tasks.check_inactive_users',
        'schedule': 86400.0,
    },
}
