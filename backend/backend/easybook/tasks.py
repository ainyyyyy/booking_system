from django.core.mail import send_mail
from celery import shared_task
from django.conf import settings


@shared_task
def send_email_task(subject, message, recipient):
    """
    A Celery task to send an email.
    """
    if message and subject and recipient:
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient],
                fail_silently=False,
            )
        except Exception as e:
            return f'Error: {e}'

        return True
    
    return False
