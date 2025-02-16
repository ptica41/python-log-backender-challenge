import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'process-outbox-every-minute': {
        'task': 'users.tasks.process_outbox_entries',
        'schedule': crontab(minute="*/1"),
    },
}
