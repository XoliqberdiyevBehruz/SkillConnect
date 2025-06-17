from django.core.mail import send_mail
from django.conf import settings

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

@shared_task
def send_reset_link(token, email, user_id):
    return send_mail(
        "Hello!",
        f"this is your reset password link: {settings.RESET_PASSWORD_LINK}/{user_id}/{token}",
        "xoliqberdiyevbehruz@gmail.com",
        [email],
        fail_silently=False,
    )