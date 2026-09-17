from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from collections import defaultdict

from dash.models import (
    Author, Article,
)
from dash.tasks.task_models import (Project, ProjectMember, Task, TaskArticle, TaskComment, ContributionLog)


# ─────────────────────────────────────────
#  Auth guard — editor must have an author profile
# ─────────────────────────────────────────

def get_author_or_redirect(request):
    """
    Returns the Author linked to the logged-in user.
    Returns None if no author profile exists.
    Use this at the top of every task view.
    """
    if not request.user.is_authenticated:
        return None
    try:
        return request.user.author_profile
    except Exception:
        return None


# ─────────────────────────────────────────
#  EDITOR DASHBOARD INDEX
#  Replaces the blank index in editor/views.py
# ─────────────────────────────────────────

def index(request):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    my_tasks    = Task.objects.filter(assigned_to=author).select_related('project')
    today       = date.today()

    task_summary = {
        'total':      my_tasks.count(),
        'todo':       my_tasks.filter(status='todo').count(),
        'inprogress': my_tasks.filter(status='inprogress').count(),
        'review':     my_tasks.filter(status='review').count(),
        'done':       my_tasks.filter(status='done').count(),
        'overdue':    my_tasks.filter(due_date__lt=today).exclude(status='done').count(),
    }

    overdue_tasks  = my_tasks.filter(due_date__lt=today).exclude(status='done').order_by('due_date')
    recent_tasks   = my_tasks.exclude(status='done').order_by('due_date')[:8]
    my_projects    = Project.objects.filter(
                        members__author=author,
                        status='active'
                     ).distinct().prefetch_related('tasks')

    # ── personal 90-day heatmap ───────────────────────────────────────
    ninety_days_ago = timezone.now() - timedelta(days=90)
    logs = ContributionLog.objects.filter(
        author=author,
        logged_at__gte=ninety_days_ago
    ).values_list('logged_at', flat=True)

    day_counts = defaultdict(int)
    for dt in logs:
        day_counts[dt.date()] += 1

    heatmap  = []
    max_day  = max(day_counts.values()) if day_counts else 1

    for i in range(89, -1, -1):
        d     = today - timedelta(days=i)
        count = day_counts.get(d, 0)
        if count == 0:        level = 0
        elif count <= max_day * 0.25: level = 1
        elif count <= max_day * 0.50: level = 2
        elif count <= max_day * 0.75: level = 3
        else:                 level = 4
        heatmap.append({'date': d, 'count': count, 'level': level})

    context = {
        'author':       author,
        'task_summary': task_summary,
        'overdue_tasks': overdue_tasks,
        'recent_tasks': recent_tasks,
        'my_projects':  my_projects,
        'heatmap':      heatmap,
        'today':        today,
    }
    return render(request, 'editor/index.html', context)


# ─────────────────────────────────────────
#  MY TASKS — full list with status filter
# ─────────────────────────────────────────

def my_tasks(request):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    tasks = Task.objects.filter(assigned_to=author).select_related('project').order_by('due_date')

    # optional filters
    status_filter  = request.GET.get('status')
    project_filter = request.GET.get('project')

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)

    today        = date.today()
    overdue      = tasks.filter(due_date__lt=today).exclude(status='done')
    my_projects  = Project.objects.filter(members__author=author, status='active').distinct()

    context = {
        'author':      author,
        'tasks':       tasks,
        'overdue':     overdue,
        'my_projects': my_projects,
        'today':       today,
    }
    return render(request, 'editor/tasks/my_tasks.html', context)


# ─────────────────────────────────────────
#  UPDATE TASK STATUS
#  Editors can only move: todo → inprogress → review
#  Done is blocked — only admin can set done
# ─────────────────────────────────────────

def update_task_status(request, id):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    task = get_object_or_404(Task, id=id, assigned_to=author)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # editors cannot mark done
        ALLOWED = ['todo', 'inprogress', 'review']
        if new_status in ALLOWED:
            task.status = new_status
            task.save()

    return redirect('/my_tasks')


# ─────────────────────────────────────────
#  TASK DETAIL — read + comment only
# ─────────────────────────────────────────

def task_detail(request, id):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    task     = get_object_or_404(Task, id=id, assigned_to=author)
    articles = task.task_articles.select_related('article')
    comments = task.comments.select_related('author').order_by('created_at')

    context = {
        'author':   author,
        'task':     task,
        'articles': articles,
        'comments': comments,
    }
    return render(request, 'editor/tasks/task_detail.html', context)


# ─────────────────────────────────────────
#  ADD COMMENT on a task
# ─────────────────────────────────────────

def add_task_comment(request, task_id):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    task = get_object_or_404(Task, id=task_id, assigned_to=author)
    body = request.POST.get('body', '').strip()

    if body:
        TaskComment.objects.create(task=task, author=author, body=body)

    return redirect(f'/task_detail/{task_id}')


# ─────────────────────────────────────────
#  MY PROJECTS — read-only view
# ─────────────────────────────────────────

def my_projects(request):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    memberships = ProjectMember.objects.filter(
        author=author
    ).select_related('project', 'project__vertical').order_by('-project__created_at')

    projects_data = []
    for m in memberships:
        p = m.project
        my_task_counts = {
            'todo':       Task.objects.filter(project=p, assigned_to=author, status='todo').count(),
            'inprogress': Task.objects.filter(project=p, assigned_to=author, status='inprogress').count(),
            'review':     Task.objects.filter(project=p, assigned_to=author, status='review').count(),
            'done':       Task.objects.filter(project=p, assigned_to=author, status='done').count(),
            'overdue':    Task.objects.filter(project=p, assigned_to=author, due_date__lt=date.today()).exclude(status='done').count(),
        }
        projects_data.append({
            'project':  p,
            'role':     m.role,
            'my_counts': my_task_counts,
        })

    context = {
        'author':        author,
        'projects_data': projects_data,
    }
    return render(request, 'editor/tasks/my_projects.html', context)


# ─────────────────────────────────────────
#  PROJECT TASKS — tasks inside one project
#  assigned to this editor only
# ─────────────────────────────────────────

def project_tasks(request, project_id):
    author  = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    project = get_object_or_404(Project, id=project_id)

    # make sure this editor is a member
    if not ProjectMember.objects.filter(project=project, author=author).exists():
        return redirect('/my_projects')

    tasks = Task.objects.filter(
        project=project,
        assigned_to=author
    ).select_related('project').order_by('due_date')

    board = {
        'todo':       tasks.filter(status='todo'),
        'inprogress': tasks.filter(status='inprogress'),
        'review':     tasks.filter(status='review'),
        'done':       tasks.filter(status='done'),
    }

    my_counts = {
        'todo':       tasks.filter(status='todo').count(),
        'inprogress': tasks.filter(status='inprogress').count(),
        'review':     tasks.filter(status='review').count(),
        'done':       tasks.filter(status='done').count(),
        'overdue':    tasks.filter(due_date__lt=date.today()).exclude(status='done').count(),
    }

    context = {
        'author':    author,
        'project':   project,
        'board':     board,
        'my_counts': my_counts,
        'today':     date.today(),
    }
    return render(request, 'editor/tasks/project_tasks.html', context)