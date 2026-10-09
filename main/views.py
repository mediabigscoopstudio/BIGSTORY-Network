from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery import shared_task
from django.utils import timezone
from .models import PasswordResetToken
from .utils import generate_reset_token
from dash.models import Enquiry,Category,Tags,Article,Author,BSTV,Newsletter,AboutPageTeams,WriterApplication
from django.db.models import Count
from django.db.models import OuterRef, Subquery
import random
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from dash.models import TrendingArticles,Unthink,Bigshot,TheChallengers,EditorsChoice,TrendingBuzz,Exclusives,ReelsHighlights,Exclusives2,LatestArticles

from django.http import HttpResponse, HttpResponsePermanentRedirect, Http404
from .utils import (
    email_executor,
    send_green_india_email,
    JUST_IN_EXCLUDED_CATEGORY_IDS,
    RESERVED_SLUGS,
    get_just_in_articles_queryset,
)

def robots_txt(request):
    content = """User-agent: *
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Googlebot-News
Allow: /

User-agent: Googlebot-Image
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: CCBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Applebot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: FacebookBot
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: Bytespider
Allow: /

User-agent: Diffbot
Allow: /

User-agent: YouBot
Allow: /

Sitemap: https://www.bigstorynetwork.com/sitemap.xml
Sitemap: https://www.bigstorynetwork.com/sitemap-news.xml
"""
    return HttpResponse(content, content_type="text/plain")

def index(request):
    trending_obj, _ = TrendingArticles.objects.get_or_create(id=1)
    selected_trending_articles = trending_obj.articles.filter(status="Enabled")
    editors_obj, _ = EditorsChoice.objects.get_or_create(id=1)
    selected_editors_articles = editors_obj.articles.all().order_by('-id')
    editors_first_two = selected_editors_articles[:2]
    editors_last = selected_editors_articles.last()
    if editors_last in editors_first_two:
        editors_last = None
    trending_buzz, _ = TrendingBuzz.objects.get_or_create(id=1)
    selected_buzz_videos = trending_buzz.videos.all().order_by('-id')
    buzz_first_two = selected_buzz_videos[:2]

    exclusives_obj, _ = Exclusives.objects.get_or_create(id=1)
    exclusive_main = exclusives_obj.main_article
    exclusive_suggestions = exclusives_obj.articles.all().order_by('-id')

    reel_highlights_obj, _ = ReelsHighlights.objects.get_or_create(id=1)
    reel_highlights = reel_highlights_obj.reels.all().order_by('-id')
    ex2_obj, _ = Exclusives2.objects.get_or_create(id=1)
    ex2_article1 = ex2_obj.article1.first()
    ex2_article2 = ex2_obj.article2.first()
    ex2_reels = ex2_obj.reels.all().order_by('-id')
    Latest_Articles = Article.objects.filter(status="Enabled").order_by('-created_at')[:4]

    context = {
        'selected_trending_articles':selected_trending_articles,
        'selected_editors_articles':selected_editors_articles,
        'editors_first_two': editors_first_two,
        'editors_last': editors_last,
        'buzz_first_two': buzz_first_two,
        'exclusive_main':exclusive_main,
        'exclusive_suggestions':exclusive_suggestions,
        'reel_highlights':reel_highlights,
        'ex2_article1':ex2_article1,
        'ex2_article2':ex2_article2,
        'ex2_reels':ex2_reels,
        'Latest_Articles':Latest_Articles,
    }
    return render(request, 'main/index.html', context)

# User Registration/ Verification/ Reseting Account/ Login Access 
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email(subject, text_content, html_content, recipient_email):
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email="Big Story Networks <info@bigstorynetwork.com>",
        to=[recipient_email],
    )
    email.attach_alternative(html_content, "text/html")  # Attach HTML content
    email.send()

def support(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Create and save the enquiry
        Enquiry.objects.create(
            name=name,
            email_id=email,
            phone_number=phone,
            subject=subject,
            message=message,
            status='Pending',
            created_at=timezone.now()
        )

        return redirect('/thank_you') 
    return render(request,'main/support.html')

def thank_you(request):
     return render(request,'main/thank_you.html')

def terms_and_conditions(request):
     return render(request,'main/terms.html')

def privacy_policy(request):
     return render(request,'main/privacy.html')

def special_pitch(request):
    bharat_one_videos = BSTV.objects.filter(category="Bharat One").order_by('-id')
    return render(request,'main/special_pitch.html',{'bharat_one_videos':bharat_one_videos})

def about_us(request):
    team_members = AboutPageTeams.objects.all()
    return render(request,'main/about.html',{'team_members':team_members})

def authors(request):
    Latest_Articles = Article.objects.order_by('-created_at')[:4]
    return render(request,'main/promotional/authors.html',{'Latest_Articles':Latest_Articles})

def advertise_with_us(request):
    return render(request,'main/promotional/business_pitch.html')

def join_newsletter(request):
    Latest_Articles = Article.objects.order_by('-created_at')[:4]
    return render(request,'main/promotional/join_newsletter.html',{'Latest_Articles':Latest_Articles})

def partner_with_us(request):
    Latest_Articles = Article.objects.order_by('-created_at')[:4]
    return render(request,'main/promotional/partner_with_us.html',{'Latest_Articles':Latest_Articles})

def career(request):
    Latest_Articles = Article.objects.order_by('-created_at')[:4]
    if request.method == "POST":
        full_name     = request.POST.get("full_name")
        email         = request.POST.get("email")
        phone         = request.POST.get("phone")
        location      = request.POST.get("location")

        experience    = request.POST.get("experience")
        track         = request.POST.get("track")

        portfolio     = request.POST.get("links")
        linkedin      = request.POST.get("linkedin")
        twitter       = request.POST.get("twitter")

        beats         = request.POST.get("beats")
        why           = request.POST.get("why")

        resume_file   = request.FILES.get("resume")
        consent_value = request.POST.get("consent") == "on"

        if not full_name or not email or not why:
            return HttpResponse("Missing required fields", status=400)

        app = WriterApplication.objects.create(
            full_name = full_name,
            email = email,
            phone = phone,
            location = location,
            experience = experience,
            track = track,
            portfolio_links = portfolio,
            linkedin = linkedin,
            twitter = twitter,
            beats = beats,
            why_bigstory = why,
            consent = consent_value
        )
        if resume_file:
            app.resume = resume_file
        app.save()
        return redirect('thank_you_applicant')

    return render(request,'main/career/career.html',{'Latest_Articles':Latest_Articles})

def thank_you_applicant(request):
    return render(request,'main/career/thank_you.html',)

def join_newsletter_form(request):
    if request.method == "POST":

        email = request.POST.get("email", "").strip().lower()

        if email:
            Newsletter.objects.get_or_create(email=email)

        return redirect("/thank_you_subscriber")

    return redirect("/")

def thank_you_subscriber(request):
    return render(request,'main/thank_you.html')

major_ids = [7, 23, 24, 25]

def the_challengers(request):
    Latest_Articles = Article.objects.filter(category__id__in=[7]).filter(status="Enabled").order_by('-created_at')
    exclusives_obj, _ = TheChallengers.objects.get_or_create(id=1)
    exclusive_main = exclusives_obj.Challanger_highlight
    exclusive_suggestions = exclusives_obj.suggested.all().order_by('-id')
    context={
        'exclusive_main':exclusive_main,
        'Latest_Articles':Latest_Articles,
        'exclusive_suggestions':exclusive_suggestions
    }
    return render(request,'main/the_challengers.html',context)

def bigshot(request):
    Latest_Articles = Article.objects.filter(category__id__in=[25]).filter(status="Enabled").order_by('-created_at')
    exclusives_obj, _ = Bigshot.objects.get_or_create(id=1)
    exclusive_main = exclusives_obj.highlight
    exclusive_suggestions = exclusives_obj.suggested.all().order_by('-id')
    context={
        'exclusive_main':exclusive_main,
        'Latest_Articles':Latest_Articles,
        'exclusive_suggestions':exclusive_suggestions
    }
    return render(request,'main/bigshot.html',context)

def unthink(request):
    Latest_Articles = Article.objects.filter(category__id__in=[23]).filter(status="Enabled").order_by('-created_at')[1:]
    exclusives_obj, _ = Unthink.objects.get_or_create(id=1)
    exclusive_main = exclusives_obj.highlight
    exclusive_suggestions = exclusives_obj.suggested.all().order_by('-id')
    context={
        'exclusive_main':exclusive_main,
        'Latest_Articles':Latest_Articles,
        'exclusive_suggestions':exclusive_suggestions
    }
    return render(request,'main/unthink.html',context)

def age_india(request):
    exclusive_main = Article.objects.filter(category__id__in=[24]).filter(status="Enabled").order_by('-created_at').first()
    Latest_Articles = Article.objects.filter(category__id__in=[24]).filter(status="Enabled").order_by('-created_at')[1:]
    exclusives_obj, _ = Exclusives.objects.get_or_create(id=1)
    exclusive_suggestions = exclusives_obj.articles.all().order_by('-id')
    context={
        'exclusive_main':exclusive_main,
        'Latest_Articles':Latest_Articles,
        'exclusive_suggestions':exclusive_suggestions
    }
    return render(request,'main/ageindia.html',context)

def bharat_one(request):
    articles = Article.objects.filter(category__id__in=[17]).filter(status="Enabled").order_by('-created_at')
    videos = BSTV.objects.filter(category="Bharat One").filter(status="Enabled").order_by('-id')
    context={
        'articles':articles,
    }
    return render(request,'main/bharat_one/index.html',{'articles':articles,'videos':videos})

from dash.green_india_models import GreenIndiaLead
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .utils import email_executor, send_green_india_email 
def Green_India(request):

    # ---------------------------------
    # FORM SUBMISSION
    # ---------------------------------
    if request.method == "POST":

        lead = GreenIndiaLead.objects.create(
            name=request.POST.get("name"),
            organisation=request.POST.get("organisation"),
            email=request.POST.get("email"),
            phone_number=request.POST.get("phone_number"),
            partnership_interest=request.POST.get("partnership_interest"),
            message=request.POST.get("message"),
        )

        email_executor.submit(send_green_india_email, lead)

        return redirect("thank_you_green_india")

    # ---------------------------------
    # GET ARTICLES FOR PAGE
    # ---------------------------------
    latest_articles = Article.objects.filter(
        category_id=26,
        status="Enabled"
    ).select_related(
        "author",
        "category"
    ).order_by("-created_at")[:10]

    featured_article = None
    list_articles = []
    trending_articles = []

    if latest_articles:
        featured_article = latest_articles[0]

    if len(latest_articles) > 1:
        list_articles = latest_articles[1:5]

    if len(latest_articles) > 5:
        trending_articles = latest_articles[5:10]

    context = {
        "featured_article": featured_article,
        "list_articles": list_articles,
        "trending_articles": trending_articles,
    }

    return render(
        request,
        "main/green_india/green_india.html",
        context
    )
def thank_you_green_india(request):    
    return render(request, "main/green_india/thank_you.html")

def category_detail(request, slug):
    if slug in RESERVED_SLUGS:
        raise Http404("Reserved slug")
    category_obj = get_object_or_404(Category, slug=slug, status__in=['Enabled', None])
    articles = Article.objects.filter(category=category_obj, status="Enabled").order_by('-created_at')
    paginator = Paginator(articles, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category_obj,
        'articles': articles,
        'page_obj': page_obj,
    }
    return render(request, 'main/category.html', context)

# Backwards-compatible alias
category = category_detail

def legacy_category_redirect(request, slug):
    category_obj = get_object_or_404(Category, slug=slug, status__in=['Enabled', None])
    return HttpResponsePermanentRedirect(category_obj.get_absolute_url())

from django.db import models
from django.utils.html import strip_tags

def render_article_detail(request, data):
    Article.objects.filter(pk=data.pk).update(views=models.F('views') + 1)
    categories = data.category 
    similar = Article.objects.filter(category=categories, status="Enabled").order_by('-created_at')[:4]
    reel_highlights_obj, _ = ReelsHighlights.objects.get_or_create(id=1)
    reel_highlights = reel_highlights_obj.reels.all().order_by('-id')[:3]
    category_ids = [7, 19, 23, 24, 25]
    new_edits = Article.objects.filter(category__id__in=category_ids, status="Enabled").order_by('-created_at')[:6]
    trending_buzz, _ = TrendingBuzz.objects.get_or_create(id=1)
    selected_buzz_videos = trending_buzz.videos.all().order_by('-id')
    buzz_first_two = selected_buzz_videos[:4]
    tags = data.tags.all()
    word_count = len(strip_tags(data.content or '').split())
    context = {
        'data': data,
        'similar': similar,
        'reel_highlights': reel_highlights,
        'new_edits': new_edits,
        'buzz_first_two': buzz_first_two,
        'tags': tags,
        'word_count': word_count,
    }
    return render(request, 'main/content.html', context)

def article_detail(request, category_slug, article_slug):
    data = get_object_or_404(
        Article.objects.select_related('category', 'author'),
        slug=article_slug,
        status="Enabled"
    )
    if not data.category or not data.category.slug:
        raise Http404("Article does not belong to requested category")

    cat_slug = data.category.slug.replace('_', '-').lower()
    req_slug = category_slug.replace('_', '-').lower()

    if cat_slug != req_slug:
        raise Http404("Article does not belong to requested category")

    return render_article_detail(request, data)

def legacy_content_redirect(request, slug):
    data = get_object_or_404(
        Article.objects.select_related('category'),
        slug=slug,
        status="Enabled"
    )
    if not data.category or not data.category.slug:
        raise Http404("Article has no valid category")
    return HttpResponsePermanentRedirect(data.get_absolute_url())

# Backwards-compatible alias
content = legacy_content_redirect

def tags(request, slug):
    tags = get_object_or_404(Tags, slug=slug)
    articles = Article.objects.filter(tags=tags, status="Enabled").order_by('-created_at')
    paginator = Paginator(articles, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    context = {
        'tags': tags,
        'articles': articles,
        'page_obj': page_obj,
    }
    return render(request, 'main/tags.html', context)

from django.core.paginator import Paginator

def just_in(request):
    trending_obj, _ = TrendingArticles.objects.get_or_create(id=1)
    selected_trending_articles = trending_obj.articles.all()
    latest_2 = Article.objects.exclude(category__id=7).filter(status="Enabled").order_by('-created_at')[:2]
    exclusives_obj, _ = Exclusives.objects.get_or_create(id=1)
    exclusive_main = exclusives_obj.main_article
    exclusive_suggestions = exclusives_obj.articles.all().order_by('-id')
    reel_highlights_obj, _ = ReelsHighlights.objects.get_or_create(id=1)
    reel_highlights = reel_highlights_obj.reels.all().order_by('-id')
    youtube_videos_latest = BSTV.objects.filter(type='Youtube')[:2]
    ex2_obj, _ = Exclusives2.objects.get_or_create(id=1)
    ex2_reels = ex2_obj.reels.all().order_by('-id')

    qs = get_just_in_articles_queryset().order_by('-created_at')
    latest = qs[0] if qs.count() > 0 else None
    second_latest = qs[1] if qs.count() > 1 else None
    remaining = qs[2:]
    paginator = Paginator(remaining, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'main/justin.html', {
        'latest_2': latest_2,
        'selected_trending_articles': selected_trending_articles,
        'exclusive_main': exclusive_main,
        'reel_highlights': reel_highlights,
        'exclusive_suggestions': exclusive_suggestions,
        'youtube_videos_latest': youtube_videos_latest,
        'latest': latest,
        'second_latest': second_latest,
        'ex2_reels': ex2_reels,
        'page_obj': page_obj
    })

def bstv(request):
    data = BSTV.objects.all().order_by('-id')
    return render(request,'main/bstv.html',{'data':data})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email_id = request.POST.get('email_id')
        phone_number = request.POST.get('phone_number')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Basic validation
        if not all([name, email_id, phone_number, subject, message]):
            messages.error(request, "Please fill in all fields.")
        else:
            # Save to DB
            enquiry = Enquiry.objects.create(
                name=name,
                email_id=email_id,
                phone_number=phone_number,
                subject=subject,
                message=message,
                status='Pending',
                created_at=timezone.now()
            )
            messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
            return redirect('/contact')
    return render(request,'main/contact.html')

def author(request, slug):
    author = get_object_or_404(Author, slug=slug)
    articles = Article.objects.filter(author=author, status="Enabled").order_by('-created_at')

    return render(request, "main/author.html", {
        "author": author,
        "articles": articles
    })


def custom_404(request, exception=None):
    """
    Custom 404 error handler.
    Fetches the top 4 latest enabled articles and renders template/404.html with status 404.
    """
    try:
        latest = (
            Article.objects.filter(status="Enabled")
            .filter(category__isnull=False)
            .exclude(category__slug="")
            .exclude(slug="")
            .select_related("category", "author")
            .order_by("-created_at")[:4]
        )
    except Exception:
        latest = []

    return render(request, "404.html", {"latest_articles": latest}, status=404)


def custom_500(request):
    """
    Custom 500 error handler.
    Fetches the top 4 latest enabled articles safely and renders template/500.html with status 500.
    """
    try:
        latest = (
            Article.objects.filter(status="Enabled")
            .filter(category__isnull=False)
            .exclude(category__slug="")
            .exclude(slug="")
            .select_related("category", "author")
            .order_by("-created_at")[:4]
        )
    except Exception:
        latest = []

    return render(request, "500.html", {"latest_articles": latest}, status=500)