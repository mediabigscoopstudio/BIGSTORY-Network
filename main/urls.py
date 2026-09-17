from django.contrib import admin
from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
# NEW: Import sitemap tools
from django.contrib.sitemaps.views import sitemap
from main.sitemaps import StaticViewSitemap, ArticleSitemap,CategorySitemap,TagsSitemap,GoogleNewsSitemap,AuthorSitemap
from main.views import robots_txt
sitemaps = {
    'static': StaticViewSitemap,
    'articles': ArticleSitemap,
    'category': CategorySitemap,
    'tags': TagsSitemap,
    'authors':AuthorSitemap,
}
news_sitemaps = {
    'news': GoogleNewsSitemap,
}
from django.http import JsonResponse
def traffic_advice(request):
    return JsonResponse([{"user_agent": "*", "disallow": False}], safe=False)
urlpatterns = [
    path("",views.index,name='index'),
    path("about_us",views.about_us,name='about_us'),
    path("age_india",views.age_india,name='age_india'),
    path("contact",views.contact,name='contact'),

    path("support",views.support,name='support'),
    path("thank_you",views.thank_you,name='thank_you'),

    path("just_in",views.just_in,name='just_in'),
    path("the_challengers",views.the_challengers,name='the_challengers'),
    path("unthink",views.unthink,name='unthink'),
    path("bigshot",views.bigshot,name='bigshot'),
    path("bharat_one",views.bharat_one,name='bharat_one'),
    path("green-india",views.Green_India,name='green-india'),
    path("thank_you_green_india",views.thank_you_green_india,name='thank_you_green_india'),

    path("terms_and_conditions",views.terms_and_conditions,name='terms_and_conditions'),
    path("privacy_policy",views.privacy_policy,name='privacy_policy'),
    path("tags/<str:slug>",views.tags,name='tags'),
    path("content/<str:slug>",views.content,name='content'),
    path("category/<str:slug>",views.category,name='category'),
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    path("advertise_with_us",views.advertise_with_us,name='advertise_with_us'),
    path("join_newsletter",views.join_newsletter,name='join_newsletter'),
    path("join_newsletter_form",views.join_newsletter_form,name='join_newsletter_form'),
    path("thank_you_subscriber",views.thank_you_subscriber,name='thank_you_subscriber'),
    path("partner_with_us",views.partner_with_us,name='partner_with_us'),
    path("career",views.career,name='career'),
    path("thank_you_applicant",views.thank_you_applicant,name='thank_you_applicant'),
    path("authors",views.authors,name='authors'),
    path("author/<str:slug>",views.author,name='author'),
    path("special_pitch",views.special_pitch,name='special_pitch'),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path('sitemap-news.xml', sitemap, 
         {'sitemaps': news_sitemaps, 'template_name': 'main/sitemap_news.xml'},
         name='sitemap-news'),
    path('favicon.ico', RedirectView.as_view(url='/static/main/Vector.png', permanent=True)),
    path('.well-known/traffic-advice', traffic_advice),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)