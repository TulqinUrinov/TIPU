import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasklar
app.conf.beat_schedule = {
    "send-payment-reminders-every-morning": {
        "task": "sms.tasks.send_payment_reminders",
        "schedule": crontab(hour=10, minute=0),  # har kuni 10:00 da
    },
}
