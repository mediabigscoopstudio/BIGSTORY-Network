import datetime
import xml.etree.ElementTree as ET
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from dash.models import Article, Category, Author, Tags


class SeoAndUrlArchitectureTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Author
        self.author = Author.objects.create(
            name="Test Author",
            designation="Senior Journalist",
            description="Author bio description",
            slug="test-author",
            status="Enabled"
        )

        # Create Standard Category
        self.category, _ = Category.objects.get_or_create(
            slug="technology",
            defaults={
                'title': "Technology",
                'description': "Technology news",
                'meta_title': "Technology News & Updates",
                'meta_description': "Latest technology updates",
                'meta_keywords': "tech, technology, gadgets",
                'status': "Enabled"
            }
        )

        # Create Category for Just In vertical slug exclusion test
        self.just_in_cat, _ = Category.objects.get_or_create(
            slug="just-in",
            defaults={
                'title': "Just In",
                'description': "Just in news",
                'meta_title': "Just In News",
                'meta_description': "Breaking news",
                'meta_keywords': "news, breaking",
                'status': "Enabled"
            }
        )

        # Create Excluded Editorial Vertical Category (ID 25: Big Shot)
        self.bigshot_cat, _ = Category.objects.get_or_create(
            id=25,
            defaults={
                'title': "Big Shot",
                'description': "Big shot business",
                'meta_title': "Big Shot",
                'meta_description': "Big Shot stories",
                'meta_keywords': "business, case studies",
                'slug': "bigshot",
                'status': "Enabled"
            }
        )

        # Create Tag
        self.tag, _ = Tags.objects.get_or_create(
            slug="ai-revolution",
            defaults={
                'title': "AI Revolution",
                'description': "AI articles",
                'meta_title': "AI News",
                'meta_description': "Artificial intelligence",
                'meta_keywords': "ai, machine learning",
                'status': "Enabled"
            }
        )

        # 1. Enabled Regular Article
        self.article_enabled = Article.objects.create(
            title="Future of Quantum Computing",
            author=self.author,
            category=self.category,
            description="Quantum computing revolutionizing cryptography.",
            meta_title="Quantum Computing Future",
            meta_description="Explore quantum computing breakthroughs.",
            meta_keywords="quantum, computing",
            slug="future-of-quantum-computing",
            status="Enabled"
        )
        self.article_enabled.tags.add(self.tag)

        # 2. Disabled Article
        self.article_disabled = Article.objects.create(
            title="Unpublished Draft Article",
            author=self.author,
            category=self.category,
            description="Draft details.",
            meta_title="Draft Article",
            meta_description="Draft article metadata.",
            meta_keywords="draft",
            slug="unpublished-draft-article",
            status="Disabled"
        )

        # 3. Enabled Just In Article (> 48 hours old)
        self.article_just_in_old = Article.objects.create(
            title="Old Breaking News from Last Week",
            author=self.author,
            category=self.category,
            description="An older breaking news story.",
            meta_title="Old Breaking News",
            meta_description="Old breaking news story.",
            meta_keywords="news, breaking",
            slug="old-breaking-news-last-week",
            status="Enabled"
        )
        # Manually backdate created_at
        Article.objects.filter(pk=self.article_just_in_old.pk).update(
            created_at=timezone.now() - datetime.timedelta(days=7)
        )

        # 4. Enabled Just In Article (< 48 hours old)
        self.article_just_in_recent = Article.objects.create(
            title="Recent Breaking News Today",
            author=self.author,
            category=self.category,
            description="A recent breaking news story.",
            meta_title="Recent Breaking News",
            meta_description="Recent breaking news story.",
            meta_keywords="news, breaking",
            slug="recent-breaking-news-today",
            status="Enabled"
        )

        # 5. Excluded Vertical Article (Bigshot ID 25)
        self.article_bigshot = Article.objects.create(
            title="Inside Big Shot Corporate Strategy",
            author=self.author,
            category=self.bigshot_cat,
            description="Analysis of a corporate titan.",
            meta_title="Corporate Strategy Breakdown",
            meta_description="Corporate titan case study.",
            meta_keywords="corporate, strategy",
            slug="inside-big-shot-corporate-strategy",
            status="Enabled"
        )

    # -------------------------------------------------------------
    # OBJECTIVE 1: /sitemap.xml
    # -------------------------------------------------------------
    def test_sitemap_xml_status_and_format(self):
        """sitemap.xml must return 200, valid XML, and use canonical https domain."""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertIn('xml', response['Content-Type'])
        content = response.content.decode('utf-8')

        # Parse valid XML
        root = ET.fromstring(response.content)
        self.assertTrue(len(root) > 0)

        # Canonical host check
        self.assertIn("https://www.bigstorynetwork.com", content)
        self.assertNotIn("<loc>http://", content)

    def test_sitemap_xml_includes_enabled_articles_with_new_url_pattern(self):
        """sitemap.xml must include enabled articles with /<category>/<article> pattern and exclude disabled."""
        response = self.client.get('/sitemap.xml')
        content = response.content.decode('utf-8')

        expected_url = f"https://www.bigstorynetwork.com/{self.category.slug}/{self.article_enabled.slug}"
        disabled_url = f"{self.article_disabled.slug}"

        self.assertIn(expected_url, content)
        self.assertNotIn(disabled_url, content)

    def test_sitemap_xml_includes_category_archives_and_excludes_just_in_category(self):
        """sitemap.xml must include regular category archives and exclude Just In category archive."""
        response = self.client.get('/sitemap.xml')
        content = response.content.decode('utf-8')

        expected_category_url = f"https://www.bigstorynetwork.com/{self.category.slug}"
        excluded_just_in_category = "https://www.bigstorynetwork.com/just-in"

        self.assertIn(expected_category_url, content)
        self.assertNotIn(excluded_just_in_category, content)

    def test_sitemap_xml_includes_tags_authors_and_static_views(self):
        """sitemap.xml must include tags, authors, and static public pages."""
        response = self.client.get('/sitemap.xml')
        content = response.content.decode('utf-8')

        self.assertIn(f"https://www.bigstorynetwork.com/tags/{self.tag.slug}", content)
        self.assertIn(f"https://www.bigstorynetwork.com/author/{self.author.slug}", content)
        self.assertIn("https://www.bigstorynetwork.com/about_us", content)
        self.assertIn("https://www.bigstorynetwork.com/contact", content)

    # -------------------------------------------------------------
    # OBJECTIVE 2: /sitemap-news.xml
    # -------------------------------------------------------------
    def test_sitemap_news_xml_contains_all_just_in_articles_without_48h_cutoff(self):
        """sitemap-news.xml must include ALL enabled Just In articles without 48h cutoff in standard XML format."""
        response = self.client.get('/sitemap-news.xml')
        self.assertEqual(response.status_code, 200)
        self.assertIn('xml', response['Content-Type'])
        content = response.content.decode('utf-8')

        # Must be standard XML, NOT news:news extension
        self.assertNotIn('<news:news>', content)
        self.assertNotIn('<news:publication>', content)

        # Must include older article (> 48h)
        self.assertIn(self.article_just_in_old.slug, content)
        # Must include recent article (< 48h)
        self.assertIn(self.article_just_in_recent.slug, content)
        # Must exclude excluded vertical article (Bigshot ID 25)
        self.assertNotIn(self.article_bigshot.slug, content)
        # Must exclude disabled article
        self.assertNotIn(self.article_disabled.slug, content)

    def test_google_news_sitemap_xml(self):
        """google-news-sitemap.xml must return 200 and contain <news:news> extension."""
        response = self.client.get('/google-news-sitemap.xml')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<news:news>', content)
        self.assertIn(self.article_just_in_recent.slug, content)

    # -------------------------------------------------------------
    # OBJECTIVE 3: URL MIGRATION & REDIRECTS
    # -------------------------------------------------------------
    def test_legacy_content_redirect_301(self):
        """Request to /content/<slug> must return HTTP 301 permanent redirect to /<category>/<slug>."""
        url = f"/content/{self.article_enabled.slug}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        expected_target = f"/{self.category.slug}/{self.article_enabled.slug}"
        self.assertEqual(response['Location'], expected_target)

    def test_legacy_category_redirect_301(self):
        """Request to /category/<slug> must return HTTP 301 permanent redirect to /<slug>."""
        url = f"/category/{self.category.slug}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        expected_target = f"/{self.category.slug}"
        self.assertEqual(response['Location'], expected_target)

    def test_legacy_content_redirect_404_for_unknown_article(self):
        """Request to /content/unknown-slug must return 404."""
        response = self.client.get('/content/unknown-slug-article')
        self.assertEqual(response.status_code, 404)

    def test_canonical_article_detail_200(self):
        """Request to /<category-slug>/<article-slug> must return 200 for matching category."""
        url = f"/{self.category.slug}/{self.article_enabled.slug}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article_enabled.title)

    def test_canonical_article_detail_404_for_wrong_category(self):
        """Request to /<wrong-category>/<article-slug> must return 404."""
        url = f"/wrong-category/{self.article_enabled.slug}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_canonical_article_detail_404_for_disabled_article(self):
        """Request to /<category-slug>/<article-slug> for disabled article must return 404."""
        url = f"/{self.category.slug}/{self.article_disabled.slug}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_canonical_category_detail_200(self):
        """Request to /<category-slug> must return 200."""
        url = f"/{self.category.slug}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.title)

    # -------------------------------------------------------------
    # MODEL URL HELPERS
    # -------------------------------------------------------------
    def test_model_get_absolute_url_methods(self):
        """Verify get_absolute_url() returns canonical URLs on Article and Category."""
        expected_article_url = f"/{self.category.slug}/{self.article_enabled.slug}"
        self.assertEqual(self.article_enabled.get_absolute_url(), expected_article_url)

        expected_category_url = f"/{self.category.slug}"
        self.assertEqual(self.category.get_absolute_url(), expected_category_url)

    # -------------------------------------------------------------
    # ROBOTS.TXT
    # -------------------------------------------------------------
    def test_robots_txt_sitemap_references(self):
        """robots.txt must return 200 and reference both canonical sitemaps."""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Sitemap: https://www.bigstorynetwork.com/sitemap.xml", content)
        self.assertIn("Sitemap: https://www.bigstorynetwork.com/sitemap-news.xml", content)
