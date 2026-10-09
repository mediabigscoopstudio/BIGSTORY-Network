# main/sitemaps.py

from datetime import timedelta
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

from dash.models import Article, Category, Tags, Author
from main.utils import get_just_in_articles_queryset


class CanonicalSiteWrapper:
    """
    Lightweight site wrapper to ensure sitemap URLs always emit
    the canonical production hostname (e.g., www.bigstorynetwork.com)
    over HTTPS, regardless of local host headers.
    """
    def __init__(self, domain):
        self.domain = domain
        self.name = 'BIGSTORY Network'


class CanonicalSitemap(Sitemap):
    """
    Base Sitemap class enforcing canonical HTTPS URLs.
    """
    protocol = 'https'

    def get_urls(self, page=1, site=None, protocol=None):
        canonical_domain = getattr(settings, 'CANONICAL_DOMAIN', 'www.bigstorynetwork.com')
        # Always use the canonical production hostname and HTTPS
        return super().get_urls(
            page=page,
            site=CanonicalSiteWrapper(canonical_domain),
            protocol='https'
        )


class StaticViewSitemap(CanonicalSitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return [
            'index',
            'about_us',
            'contact',
            'support',
            'just_in',
            'the_challengers',
            'unthink',
            'bigshot',
            'age_india',
            'bharat_one',
            'green-india',
            'authors',
            'career',
            'advertise_with_us',
            'join_newsletter',
            'partner_with_us',
            'terms_and_conditions',
            'privacy_policy',
        ]

    def location(self, item):
        return reverse(item)


class CategorySitemap(CanonicalSitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        # Include enabled category archives, excluding Just In (served via /just-in)
        return (
            Category.objects.filter(status__in=['Enabled', None])
            .exclude(slug__in=['just-in', 'just_in'])
            .exclude(title__iexact='just in')
            .exclude(slug='')
            .order_by('id')
        )

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.created_at


class ArticleSitemap(CanonicalSitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        # All enabled articles regardless of age, with category and author pre-fetched
        return (
            Article.objects.filter(status="Enabled")
            .filter(category__isnull=False)
            .exclude(category__slug="")
            .exclude(slug="")
            .select_related("category", "author")
            .order_by("-updated_at")
        )

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at


class TagsSitemap(CanonicalSitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return (
            Tags.objects.filter(status__in=['Enabled', None])
            .exclude(slug='')
            .order_by('id')
        )

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.created_at


class AuthorSitemap(CanonicalSitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return (
            Author.objects.filter(status__in=['Enabled', None])
            .exclude(status='Disabled')
            .exclude(slug='')
            .order_by('id')
        )

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.created_at


class JustInArticleSitemap(CanonicalSitemap):
    """
    Standard XML sitemap for ALL enabled Just In articles.
    Contains both older and recent articles without any 48-hour cutoff.
    Rendered using standard sitemap format (no <news:news> extension).
    """
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return get_just_in_articles_queryset().order_by('-created_at')

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at


class GoogleNewsJustInSitemap(CanonicalSitemap):
    """
    Dedicated Google News extension sitemap for recent articles published
    within the last 48 hours, capped at 1,000 URLs per Google specification.
    """
    changefreq = 'daily'
    priority = 0.9
    limit = 1000

    def items(self):
        cutoff = timezone.now() - timedelta(hours=48)
        return (
            get_just_in_articles_queryset()
            .filter(created_at__gte=cutoff)
            .order_by('-created_at')[:1000]
        )

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.created_at