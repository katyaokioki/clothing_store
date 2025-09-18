from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

@shared_task
def send_daily_promotions():
    subject = "Ежедневные акции"
    body = f"Подборка на {timezone.now().date().isoformat()}"
    recipients = ["test@example.com"]  # TODO: заменить на реальные адреса/выборку из БД
    send_mail(subject, body, "no-reply@fashionstore.local", recipients)
    return "ok"
