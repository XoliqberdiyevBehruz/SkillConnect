from django.core.mail import send_mail

from celery import shared_task

from apps.accounts import models


@shared_task
def send_code_to_email(code, mail):
    return send_mail(
        "Salom!",
        f"Sizning tasdiqlash kodingiz: {code}",
        "xoliqberdiyevbehruz@gmail.com",
        [mail],
        fail_silently=False
    )
