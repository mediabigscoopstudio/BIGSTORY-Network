from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# ---------------- User Profile ----------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='profiles/')
    def __str__(self):
        return self.user.username


# ---------------- Categories ----------------
class Category(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()
    meta_keywords = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100,blank=True, null=True,default="Enabled")
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.slug:
            try:
                return reverse('category_direct', kwargs={'slug': self.slug})
            except Exception:
                return reverse('category_direct', urlconf='main.urls', kwargs={'slug': self.slug})
        return f"/category/{self.id}"

    def __str__(self):
        return self.title

# ---------------- Categories ----------------
class Tags(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()
    meta_keywords = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100,blank=True, null=True,default="Enabled")
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        try:
            return reverse('tags', kwargs={'slug': self.slug})
        except Exception:
            return reverse('tags', urlconf='main.urls', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

# ---------------- Authors ----------------
class Author(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="author_profile",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    description = models.TextField()
    email = models.EmailField(unique=True,blank=True, null=True)
    DOB = models.DateField(unique=True,blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='authors/')
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100,blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':  # Generate slug only if it's empty
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Author.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{count}'
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        try:
            return reverse('author', kwargs={'slug': self.slug})
        except Exception:
            return reverse('author', urlconf='main.urls', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

class AboutPageTeams(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    image = models.ImageField(upload_to='about_us/')
    def __str__(self):
        return self.name

# ---------------- Articles ----------------
class Article(models.Model):
    title = models.CharField(max_length=1500)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tags', related_name='articles', blank=True)
    description = models.TextField(blank=True,null=True)
    tldr_title = models.CharField(max_length=1500,blank=True, null=True)
    tldr = models.TextField(blank=True,null=True)
    meta_title = models.CharField(max_length=1500)
    meta_description = models.TextField()
    meta_keywords = models.CharField(max_length=1500)
    content = models.TextField(blank=True, null=True)
    likes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, blank=True,max_length=1500)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100,blank=True, null=True,default="Enabled")
    title_colour = models.CharField(max_length=100,blank=True)
    banner_background_colour = models.CharField(max_length=100,blank=True)
    remaining_text_colour = models.CharField(max_length=100,blank=True)
    banner_image = models.ImageField(upload_to='articles/banners/', blank=True, null=True)
    thumbnail_image = models.ImageField(upload_to='articles/thumbnails/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        # Create slug if missing
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            count = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        # ✅ Ensure Django actually saves the object
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.category and getattr(self.category, 'slug', None) and self.slug:
            try:
                return reverse('article_detail', kwargs={
                    'category_slug': self.category.slug,
                    'article_slug': self.slug
                })
            except Exception:
                return reverse('article_detail', urlconf='main.urls', kwargs={
                    'category_slug': self.category.slug,
                    'article_slug': self.slug
                })
        if self.slug:
            try:
                return reverse('content', kwargs={'slug': self.slug})
            except Exception:
                return reverse('content', urlconf='main.urls', kwargs={'slug': self.slug})
        return f"/content/{self.id}"

    def __str__(self):
        return self.title

class ArticleFAQ(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=500)
    answer = models.TextField()

    def __str__(self):
        return self.question
    
class ArticleHowTo(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="howto_steps")
    step_name = models.CharField(max_length=300)
    step_text = models.TextField()

    def __str__(self):
        return self.step_name


class BSTV(models.Model):
    title = models.CharField(max_length=3000)
    link = models.URLField()
    category = models.CharField(max_length=255)
    type = models.CharField(max_length=255,default="Reel")
    description = models.TextField()
    status = models.CharField(max_length=100,blank=True, null=True,default="Enabled")
    slug = models.SlugField(unique=True, blank=True)
    thumbnail_image = models.ImageField(upload_to='bstv/thumbnails/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            count = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{count}'
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# ---------------- Newsletter ----------------
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email


# ---------------- Ad Management ----------------
class Ad(models.Model):
    title = models.CharField(max_length=255,null=True,blank=True)
    image = models.ImageField(upload_to='ads/')
    url = models.URLField()
    clicks = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return f"{self.type} - {self.url}"


# ---------------- Enquiry ----------------
class Enquiry(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    name = models.CharField(max_length=100)
    email_id = models.EmailField()
    phone_number = models.CharField(max_length=15)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, default='Pending', choices=STATUS_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
class TrendingArticles(models.Model):
    articles = models.ManyToManyField(Article, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Trending Articles"
        verbose_name_plural = "Trending Articles"

    def __str__(self):
        return "Trending Articles Selection"

class EditorsChoice(models.Model):
    articles = models.ManyToManyField(Article, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Editor's Choice"
        verbose_name_plural = "Editor's Choice"

    def __str__(self):
        return "Editor's Choice Selection"
    
class TrendingBuzz(models.Model):
    videos = models.ManyToManyField(BSTV, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Trending Buzz Videos"
        verbose_name_plural = "Trending Buzz Videos"

    def __str__(self):
        return "Trending Buzz Selection"

class Exclusives(models.Model):
    main_article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="exclusive_main",
        limit_choices_to={'status': 'Enabled'},
        blank=True,
        null=True
    )
    articles = models.ManyToManyField(
        Article,
        related_name="exclusive_articles",
        limit_choices_to={'status': 'Enabled'},
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Exclusives"
        verbose_name_plural = "Exclusives"

    def __str__(self):
        return "Exclusive Section Selection"

class ReelsHighlights(models.Model):
    reels = models.ManyToManyField(
        BSTV,
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reels Highlights"
        verbose_name_plural = "Reels Highlights"

    def __str__(self):
        return "Reels Highlights Selection"
    
class Exclusives2(models.Model):
    article1 = models.ManyToManyField(Article, related_name="article1", limit_choices_to={'status': 'Enabled'}, blank=True)
    article2 = models.ManyToManyField(Article, related_name="article2", limit_choices_to={'status': 'Enabled'}, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    reels = models.ManyToManyField(
        BSTV,
        blank=True
    )

    class Meta:
        verbose_name = "Exclusives2"
        verbose_name_plural = "Exclusives2"

    def __str__(self):
        return "Exclusives2"
    
class LatestArticles(models.Model):
    article = models.ManyToManyField(Article, related_name="latestArticles", limit_choices_to={'status': 'Enabled'}, blank=True)

    class Meta:
        verbose_name = "Latest Articles"
        verbose_name_plural = "Latest Articles"

    def __str__(self):
        return "Latest Articles Selection"
    

class TheChallengers(models.Model):
    Challanger_highlight = models.ForeignKey(Article,on_delete=models.CASCADE,related_name="challenger_highlight",blank=True,null=True)
    suggested = models.ManyToManyField(Article, related_name="Challengers_Suggestion", blank=True)

    class Meta:
        verbose_name = "TheChallengers Highlights"
        verbose_name_plural = "TheChallengers Highlights"

    def __str__(self):
        return "TheChallengers Highlights Selection"
    
class Bigshot(models.Model):
    highlight = models.ForeignKey(Article,on_delete=models.CASCADE,related_name="bigshot_highlight",blank=True,null=True)
    suggested = models.ManyToManyField(Article, related_name="Bigshot_Suggestion", blank=True)

    class Meta:
        verbose_name = "Bigshot Highlights"
        verbose_name_plural = "Bigshot Highlights"

    def __str__(self):
        return "Bigshot Highlights Selection"
    
class Unthink(models.Model):
    highlight = models.ForeignKey(Article,on_delete=models.CASCADE,related_name="Unthink_highlight",blank=True,null=True)
    suggested = models.ManyToManyField(Article, related_name="Unthink_Suggestion", blank=True)

    class Meta:
        verbose_name = "unthinnk Highlights"
        verbose_name_plural = "unthinnk Highlights"

    def __str__(self):
        return "unthinnk Highlights Selection"


class WriterApplication(models.Model):
    EXPERIENCE_CHOICES = [
        ("student", "Student / Campus"),
        ("fresher", "Fresher (0–1 year)"),
        ("junior", "1–3 years"),
        ("mid", "3+ years"),
    ]

    TRACK_CHOICES = [
        ("breaking", "Daily news / breaking"),
        ("explainer", "Explainers & analysis"),
        ("opinion", "Opinion & columns"),
        ("features", "Features & longform"),
        ("script", "Video scripts / BSTV"),
        ("open", "Open to anything exciting"),
    ]

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=120, blank=True, null=True)

    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, blank=True, null=True)
    track = models.CharField(max_length=20, choices=TRACK_CHOICES, blank=True, null=True)

    portfolio_links = models.TextField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)

    beats = models.CharField(max_length=300, blank=True, null=True)

    why_bigstory = models.TextField()

    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    consent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.email})"