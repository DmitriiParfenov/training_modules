from celery import shared_task
from django.core.mail import send_mail

from config import settings


@shared_task
def send_email_creation(email, module):
    """Метод отправляет сообщение о создании модуля на указанный адрес электронной почты."""

    send_mail(
        subject='Создание модуля для обучения',
        message=f'Здравствуйте, {email}!\n\n'
                f'На портале 127.0.0.1 вы создали курс —  {module}!\n\n'
                f'С уважением, администрация сайта!',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False
    )
