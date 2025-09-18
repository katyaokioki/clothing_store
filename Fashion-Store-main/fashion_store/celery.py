import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fashion_store.settings")
app = Celery("fashion_store")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send-promotions-every-morning": {
        "task": "catalog.tasks.send_daily_promotions",
        "schedule": crontab(minute="*/1"),  # каждый день в 07:00 UTC
    }
}