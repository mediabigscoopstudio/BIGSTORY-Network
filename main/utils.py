import string, random

def generate_reset_token(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# utils.py

from concurrent.futures import ThreadPoolExecutor
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Max 10 emails sending at same time
email_executor = ThreadPoolExecutor(max_workers=10)


def send_green_india_email(lead):
    subject = "Thank You for Your Interest in Green India | BIGSTORY Network"

    html_content = render_to_string(
        "main/green_india/email.html",
        {
            "lead": lead
        }
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body="Thank you for contacting Green India.",
        from_email="BIGSTORY Network | Green India <ceo@bigstorynetwork.com>",
        to=[lead.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)