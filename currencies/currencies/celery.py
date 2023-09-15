from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'currencies.settings')

app = Celery('currencies')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'get_daily_quotes': {
        'task': 'quotes.tasks.get_quotes',
        'schedule': crontab(hour='12', minute='0')
    },
    'check_limits': {
        'task': 'quotes.tasks.check_limits',
        'schedule': crontab(hour='12', minute='5')
    }
}
