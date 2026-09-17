# Run this inside: python manage.py shell
# Then call:
# send_podcast_invite()

from concurrent.futures import ThreadPoolExecutor
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


# Max 5 invites at same time
executor = ThreadPoolExecutor(max_workers=5)


def _send_invite(email_address):
    subject = "An Exclusive Invitation to Join the BIGSTORY Podcast"

    html_content = render_to_string(
        "main/email_campaign/podcast_invite.html"
    )

    mail = EmailMultiAlternatives(
        subject=subject,
        body="You have been invited to join the BIGSTORY Podcast.",
        from_email="BIGSTORY Network <ceo@bigstorynetwork.com>",
        to=[email_address],
        reply_to=["ceo@bigstorynetwork.com"],
    )

    mail.attach_alternative(html_content, "text/html")
    mail.send(fail_silently=False)


def send_podcast_invite():
    email_address = input("Enter recipient email: ").strip().lower()

    if not email_address:
        print("No email entered.")
        return

    executor.submit(_send_invite, email_address)

    print(f"Invite queued successfully for {email_address}")