from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from ..models import Author, Category, Article,BSTV


# ─────────────────────────────────────────
#  Project
# ─────────────────────────────────────────

class Project(models.Model):

    STATUS_CHOICES = [
        ('active',   'Active'),
        ('archived', 'Archived'),
    ]

    # 9 curated presets — admin can also type any hex
    COLOR_PRESETS = [
        ('#534AB7', 'Purple'),
        ('#0F6E56', 'Teal'),
        ('#993C1D', 'Coral'),
        ('#993556', 'Pink'),
        ('#185FA5', 'Blue'),
        ('#3B6D11', 'Green'),
        ('#854F0B', 'Amber'),
        ('#A32D2D', 'Red'),
        ('#5F5E5A', 'Gray'),
    ]

    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    vertical    = models.ForeignKey(
                    Category,
                    on_delete=models.SET_NULL,
                    null=True, blank=True,
                    related_name='projects',
                    help_text='Maps to your existing Category (BIG SHOT, UN THiNK, etc.)'
                  )
    color_hex   = models.CharField(
                    max_length=7,
                    default='#534AB7',
                    help_text='Hex color for project card accent. Choose a preset or enter any #RRGGBB.'
                  )
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by  = models.ForeignKey(
                    User,
                    on_delete=models.SET_NULL,
                    null=True,
                    related_name='created_projects'
                  )
    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.name

    def task_counts(self):
        """Returns a dict of task counts by status for quick dashboard use."""
        qs = self.tasks.all()
        return {
            'todo':       qs.filter(status='todo').count(),
            'inprogress': qs.filter(status='inprogress').count(),
            'review':     qs.filter(status='review').count(),
            'done':       qs.filter(status='done').count(),
            'total':      qs.count(),
            'overdue':    qs.filter(due_date__lt=timezone.now().date())
                            .exclude(status='done').count(),
        }


# ─────────────────────────────────────────
#  ProjectMember
# ─────────────────────────────────────────

class ProjectMember(models.Model):

    ROLE_CHOICES = [
        ('lead',   'Lead'),
        ('member', 'Member'),
    ]

    project   = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    author    = models.ForeignKey(Author,  on_delete=models.CASCADE, related_name='project_memberships')
    role      = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('project', 'author')
        verbose_name = 'Project Member'
        verbose_name_plural = 'Project Members'

    def __str__(self):
        return f'{self.author.name} → {self.project.name} ({self.role})'


# ─────────────────────────────────────────
#  Task
# ─────────────────────────────────────────

class Task(models.Model):

    STATUS_CHOICES = [
        ('todo',       'To Do'),
        ('inprogress', 'In Progress'),
        ('review',     'Review'),
        ('done',       'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
        ('urgent', 'Urgent'),
    ]

    TYPE_CHOICES = [
        ('article', 'Article Assignment'),
        ('seo',     'SEO Task'),
        ('social',  'Social Media'),
        ('general', 'General'),
    ]
    PLATFORM_CHOICES = [
    ('website',  'Website'),
    ('linkedin', 'LinkedIn'),
    ('meta',     'Meta'),
    ('youtube',  'YouTube'),
    ]

    title       = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(
                    Author,
                    on_delete=models.SET_NULL,
                    null=True, blank=True,
                    related_name='assigned_tasks'
                  )
    created_by  = models.ForeignKey(
                    User,
                    on_delete=models.SET_NULL,
                    null=True,
                    related_name='created_tasks'
                  )
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority    = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    task_type   = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    due_date    = models.DateField(null=True, blank=True)
    deploy_date     = models.DateField(null=True, blank=True)
    deploy_platform = models.CharField(
                    max_length=20,
                    choices=PLATFORM_CHOICES,
                    null=True,
                    blank=True
                  )
    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-priority']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return f'{self.title} [{self.get_status_display()}]'

    @property
    def is_overdue(self):
        if self.due_date and self.status != 'done':
            return self.due_date < timezone.now().date()
        return False


# ─────────────────────────────────────────
#  TaskArticle  (Task ↔ Article junction)
# ─────────────────────────────────────────

class TaskArticle(models.Model):
    task        = models.ForeignKey(Task,    on_delete=models.CASCADE, related_name='task_articles')
    article     = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='task_articles')
    attached_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('task', 'article')
        verbose_name = 'Task Article'
        verbose_name_plural = 'Task Articles'

    def __str__(self):
        return f'{self.task.title} ← {self.article.title}'


# ─────────────────────────────────────────
#  TaskComment
# ─────────────────────────────────────────

class TaskComment(models.Model):
    task       = models.ForeignKey(Task,   on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='task_comments')
    body       = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Task Comment'
        verbose_name_plural = 'Task Comments'

    def __str__(self):
        return f'{self.author.name} on "{self.task.title}"'


# ─────────────────────────────────────────
#  ContributionLog  (powers the heatmap)
# ─────────────────────────────────────────

class ContributionLog(models.Model):

    ACTION_CHOICES = [
        ('draft_saved',        'Draft Saved'),
        ('article_published',  'Article Published'),
        ('task_done',          'Task Marked Done'),
    ]

    author    = models.ForeignKey(Author,  on_delete=models.CASCADE, related_name='contributions')
    project   = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contributions')
    action    = models.CharField(max_length=30, choices=ACTION_CHOICES)
    article   = models.ForeignKey(
                  Article,
                  on_delete=models.SET_NULL,
                  null=True, blank=True,
                  related_name='contribution_logs',
                  help_text='Populated for article-related actions; null for task_done.'
                )
    task      = models.ForeignKey(
                  Task,
                  on_delete=models.SET_NULL,
                  null=True, blank=True,
                  related_name='contribution_logs',
                  help_text='Populated for task_done; null for article actions.'
                )
    logged_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-logged_at']
        verbose_name = 'Contribution Log'
        verbose_name_plural = 'Contribution Logs'

    def __str__(self):
        return f'{self.author.name} · {self.get_action_display()} · {self.logged_at.date()}'
    

# ─────────────────────────────────────────
#  PASTE INSTRUCTIONS
#  1. In your existing Task model, REPLACE the TYPE_CHOICES with the expanded version below.
#  2. Add the TaskBSTV model after TaskArticle.
#  3. Run: python manage.py makemigrations dash && python manage.py migrate
# ─────────────────────────────────────────


# ── 1. Replace Task.TYPE_CHOICES with this ───────────────────────────────────

TYPE_CHOICES = [
    ('article',      'Article Assignment'),
    ('seo',          'SEO Task'),
    ('social',       'Social Media'),
    ('general',      'General'),
    ('video_shoot',  'Video — Shoot'),
    ('video_edit',   'Video — Edit'),
    ('video_upload', 'Video — Upload'),
    ('reel',         'Reel'),
    ('youtube',      'YouTube'),
    ('calendar',     'Content Calendar'),
]


# ── 2. Add this model after TaskArticle ──────────────────────────────────────

class TaskBSTV(models.Model):
    """
    Junction table — one Task can have zero or many BSTV videos attached.
    Mirrors TaskArticle exactly but points to BSTV instead of Article.
    Content team attaches videos during or after task creation.
    """
    task        = models.ForeignKey(
                    Task,
                    on_delete=models.CASCADE,
                    related_name='task_bstvs'
                  )
    bstv        = models.ForeignKey(
                    BSTV,
                    on_delete=models.CASCADE,
                    related_name='task_bstvs'
                  )
    attached_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('task', 'bstv')
        verbose_name        = 'Task BSTV'
        verbose_name_plural = 'Task BSTVs'

    def __str__(self):
        return f'{self.task.title} ← {self.bstv.title}'


# ── 3. Add to dash/admin.py ──────────────────────────────────────────────────
# admin.site.register(TaskBSTV)