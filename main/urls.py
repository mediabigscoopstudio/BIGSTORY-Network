from django.contrib import admin
from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.contrib.sitemaps.views import sitemap
from main.sitemaps import (
    StaticViewSitemap,
    ArticleSitemap,
    CategorySitemap,
    TagsSitemap,
    AuthorSitemap,
    JustInArticleSitemap,
    GoogleNewsJustInSitemap,
)
from main.views import robots_txt

sitemaps = {
    'static': StaticViewSitemap,
    'articles': ArticleSitemap,
    'category': CategorySitemap,
    'tags': TagsSitemap,
    'authors': AuthorSitemap,
}

news_sitemaps = {
    'just_in': JustInArticleSitemap,
}

google_news_sitemaps = {
    'news': GoogleNewsJustInSitemap,
}

from django.http import JsonResponse
def traffic_advice(request):
    return JsonResponse([{"user_agent": "*", "disallow": False}], safe=False)

urlpatterns = [
    # Homepage
    path("", views.index, name='index'),

    # Public Editorial & Informational Static Pages
    path("about_us", views.about_us, name='about_us'),
    path("age_india", views.age_india, name='age_india'),
    path("contact", views.contact, name='contact'),
    path("support", views.support, name='support'),
    path("thank_you", views.thank_you, name='thank_you'),

    # Editorial Verticals
    path("just_in", views.just_in, name='just_in'),
    path("just-in", views.just_in, name='just-in'),
    path("the_challengers", views.the_challengers, name='the_challengers'),
    path("unthink", views.unthink, name='unthink'),
    path("bigshot", views.bigshot, name='bigshot'),
    path("bharat_one", views.bharat_one, name='bharat_one'),
    path("green-india", views.Green_India, name='green-india'),
    path("thank_you_green_india", views.thank_you_green_india, name='thank_you_green_india'),

    path("terms_and_conditions", views.terms_and_conditions, name='terms_and_conditions'),
    path("privacy_policy", views.privacy_policy, name='privacy_policy'),

    path("tags/<str:slug>", views.tags, name='tags'),
    path("author/<str:slug>", views.author, name='author'),

    # Legacy routes with permanent 301 redirects to new canonical architecture
    path("content/<str:slug>", views.legacy_content_redirect, name='content'),
    path("category/<str:slug>", views.legacy_category_redirect, name='category'),

    # Sitemaps
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    # /sitemap-news.xml: Standard XML sitemap containing all enabled Just In articles (no 48h cutoff)
    path("sitemap-news.xml", sitemap, {'sitemaps': news_sitemaps}, name='sitemap-news'),
    # /google-news-sitemap.xml: Dedicated Google News XML sitemap for recent articles (< 48h)
    path("google-news-sitemap.xml", sitemap,
         {'sitemaps': google_news_sitemaps, 'template_name': 'main/sitemap_news.xml'},
         name='google-news-sitemap'),

    path("advertise_with_us", views.advertise_with_us, name='advertise_with_us'),
    path("join_newsletter", views.join_newsletter, name='join_newsletter'),
    path("join_newsletter_form", views.join_newsletter_form, name='join_newsletter_form'),
    path("thank_you_subscriber", views.thank_you_subscriber, name='thank_you_subscriber'),
    path("partner_with_us", views.partner_with_us, name='partner_with_us'),
    path("career", views.career, name='career'),
    path("thank_you_applicant", views.thank_you_applicant, name='thank_you_applicant'),
    path("authors", views.authors, name='authors'),
    path("special_pitch", views.special_pitch, name='special_pitch'),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("favicon.ico", RedirectView.as_view(url='/static/main/Vector.png', permanent=True)),
    path(".well-known/traffic-advice", traffic_advice),

    # New Canonical Category Archive route: /<category-slug>
    path("<str:slug>", views.category_detail, name='category_direct'),

    # New Canonical Article Detail route: /<category-slug>/<article-slug>
    path("<str:category_slug>/<str:article_slug>", views.article_detail, name='article_detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)