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


# -------------------------------------------------------------
# SEO & Editorial Architecture Helpers
# -------------------------------------------------------------

# Dedicated editorial vertical category IDs:
# 7: The Challengers (/the_challengers)
# 23: Unthink (/unthink)
# 24: Age India (/age_india)
# 25: Big Shot (/bigshot)
# 26: Green India (/green-india)
JUST_IN_EXCLUDED_CATEGORY_IDS = [7, 23, 24, 25, 26]

# Slugs reserved by top-level routes to prevent route collisions
RESERVED_SLUGS = {
    'admin', 'static', 'media', 'sitemap', 'sitemap.xml',
    'sitemap-news', 'sitemap-news.xml', 'google-news-sitemap.xml',
    'robots', 'robots.txt', 'favicon.ico',
    'about_us', 'contact', 'support', 'thank_you',
    'terms_and_conditions', 'privacy_policy',
    'just_in', 'just-in', 'the_challengers', 'unthink', 'bigshot',
    'age_india', 'bharat_one', 'green-india', 'thank_you_green_india',
    'authors', 'career', 'advertise_with_us', 'join_newsletter',
    'join_newsletter_form', 'thank_you_subscriber', 'thank_you_applicant',
    'partner_with_us', 'tags', 'content', 'category', 'author', 'special_pitch'
}


def get_just_in_articles_queryset():
    """
    Centralized definition of Just In articles.
    Returns all enabled articles that do not belong to the dedicated editorial
    vertical categories (7, 23, 24, 25, 26), ensuring valid category and slug.
    """
    from dash.models import Article
    return Article.objects.filter(
        status="Enabled"
    ).exclude(
        category__id__in=JUST_IN_EXCLUDED_CATEGORY_IDS
    ).filter(
        category__isnull=False
    ).exclude(
        category__slug=""
    ).exclude(
        slug=""
    ).select_related('category', 'author')