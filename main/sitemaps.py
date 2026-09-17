# main/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from dash.models import Article  # or your content model

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return [
            'index', 'about_us', 'age_india', 'contact', 'support',
            'just_in', 'the_challengers', 'unthink', 'bigshot',
            'bharat_one', 'Green_India', 'authors', 'career',
            'advertise_with_us', 'join_newsletter', 'partner_with_us',
            'terms_and_conditions', 'privacy_policy',
        ]

    def location(self, item):
        return reverse(item)


class ArticleSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        from dash.models import Article
        return Article.objects.filter(status="Enabled").order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        from dash.models import Category  # adjust if your model is named differently
        return Category.objects.all()

    def lastmod(self, obj):
        return obj.created_at  # or obj.created_at if updated_at doesn't exist
    
class TagsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        from dash.models import Tags  # adjust if your model is named differently
        return Tags.objects.all()

    def lastmod(self, obj):
        return obj.created_at  # or obj.created_at if updated_at doesn't exist
    
from django.utils import timezone
from datetime import timedelta

class GoogleNewsSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9
    limit = 1000  # Google limits news sitemaps to 1,000 URLs

    def items(self):
        # 1. Calculate the cutoff time (48 hours ago)
        cutoff = timezone.now() - timedelta(hours=48)
        
        # 2. Filter articles: Must be newer than 48 hours
        # Note: Ensure you are filtering by 'published' date if you have drafts
        return Article.objects.filter(created_at__gte=cutoff).order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at
    
class AuthorSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        from dash.models import Author
        return Author.objects.filter(status__in=['Enabled', None]).exclude(status='Disabled')

    def lastmod(self, obj):
        return obj.created_at