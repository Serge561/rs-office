"""Функционал формы отправки обратной связи."""

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


def send_contact_email_message(subject, email, content, ip, user_id):
    """
    Function to send contact form email
    """
    user = User.objects.get(id=user_id) if user_id else None
    message = render_to_string(
        "system/email/feedback_email_send.html",
        {
            "email": email,
            "content": content,
            "ip": ip,
            "user": user,
        },
    )
    email = EmailMessage(
        subject, message, settings.EMAIL_SERVER, [settings.EMAIL_ADMIN]
    )  # noqa: E501
    email.send(fail_silently=False)
