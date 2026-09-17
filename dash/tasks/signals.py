from django.db.models.signals import post_save
from django.dispatch import receiver
from dash.models import Article, Author
from .task_models import ContributionLog, Task


# ─────────────────────────────────────────
#  Article saved → log draft_saved or article_published
# ─────────────────────────────────────────

@receiver(post_save, sender=Article)
def log_article_contribution(sender, instance, created, **kwargs):
    """
    Fires every time an Article is saved.
    - Any save (including creation) → draft_saved
    - If status is 'Enabled' → article_published  (replaces draft_saved for that action)

    We only log if:
    1. The Article's author has a linked User (author.user is not None)
    2. The author is a member of at least one active Project

    The log is written once per save, not once per project — we pick the
    most relevant project (the one whose vertical matches the article's
    category, falling back to the first active project the author is in).
    """
    author = instance.author

    # find all active projects this author is a member of
    from .task_models import ProjectMember, Project
    memberships = ProjectMember.objects.filter(
        author=author,
        project__status='active'
    ).select_related('project', 'project__vertical')

    if not memberships.exists():
        return  # author is not assigned to any active project — skip

    # pick best-matching project: same vertical as article's category first
    project = None
    for m in memberships:
        if m.project.vertical and m.project.vertical == instance.category:
            project = m.project
            break
    if not project:
        project = memberships.first().project

    # determine action
    action = 'article_published' if instance.status == 'Enabled' else 'draft_saved'

    ContributionLog.objects.create(
        author=author,
        project=project,
        action=action,
        article=instance,
    )


# ─────────────────────────────────────────
#  Task status → done → log task_done
#  (also handled inline in update_task_status view,
#   but this signal covers edits done via Django admin)
# ─────────────────────────────────────────

@receiver(post_save, sender=Task)
def log_task_done(sender, instance, created, **kwargs):
    """
    Fires when a Task is saved with status='done'.
    Skips if no author is assigned.
    Avoids duplicate logs by checking if a task_done entry already exists
    for this task within the last minute (handles both view + admin saves).
    """
    if instance.status != 'done' or not instance.assigned_to:
        return

    from django.utils import timezone
    from datetime import timedelta

    one_minute_ago = timezone.now() - timedelta(minutes=1)
    already_logged = ContributionLog.objects.filter(
        task=instance,
        action='task_done',
        logged_at__gte=one_minute_ago,
    ).exists()

    if not already_logged:
        ContributionLog.objects.create(
            author=instance.assigned_to,
            project=instance.project,
            action='task_done',
            task=instance,
        )