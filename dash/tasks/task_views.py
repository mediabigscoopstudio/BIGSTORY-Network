from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from datetime import date, timedelta
from collections import defaultdict

from dash.models import Author, Category, Article, BSTV
from dash.tasks.task_models import (
    Project, ProjectMember, Task, TaskArticle, TaskBSTV,
    TaskComment, ContributionLog
)


def superadmin_required(user):
    return user.is_superuser


# ─────────────────────────────────────────
#  DASHBOARD INDEX
# ─────────────────────────────────────────

@user_passes_test(superadmin_required, login_url='/login_view')
def index(request):
    projects      = Project.objects.filter(status='active').prefetch_related('members', 'tasks')
    all_tasks     = Task.objects.select_related('project', 'assigned_to')
    overdue_tasks = all_tasks.filter(due_date__lt=date.today()).exclude(status='done')
    authors       = Author.objects.filter(status='Enabled')

    task_summary = {
        'total':      all_tasks.count(),
        'todo':       all_tasks.filter(status='todo').count(),
        'inprogress': all_tasks.filter(status='inprogress').count(),
        'review':     all_tasks.filter(status='review').count(),
        'done':       all_tasks.filter(status='done').count(),
        'overdue':    overdue_tasks.count(),
    }

    for project in projects:
        project.counts = project.task_counts()

    # production calendar — tasks with a due_date (all tasks)
    prod_tasks = Task.objects.filter(
        due_date__isnull=False
    ).select_related('project').order_by('due_date')

    # content calendar — tasks with a deploy_date set
    deploy_tasks = Task.objects.filter(
        deploy_date__isnull=False
    ).select_related('project').order_by('deploy_date')

    context = {
        'projects':      projects,
        'task_summary':  task_summary,
        'overdue_tasks': overdue_tasks.order_by('due_date')[:10],
        'authors':       authors,
        'all_tasks':     prod_tasks,    # feeds production calendar
        'deploy_tasks':  deploy_tasks,  # feeds content calendar
    }
    return render(request, 'dash/index.html', context)
# ─────────────────────────────────────────
#  PROJECTS
# ─────────────────────────────────────────

@user_passes_test(superadmin_required, login_url='/login_view')
def projects(request):
    all_projects = Project.objects.all().prefetch_related('members', 'tasks')
    for p in all_projects:
        p.counts = p.task_counts()
    return render(request, 'dash/projects/projects.html', {'projects': all_projects})


@user_passes_test(superadmin_required, login_url='/login_view')
def add_project(request):
    authors       = Author.objects.filter(status='Enabled')
    categories    = Category.objects.filter(status='Enabled')
    color_presets = Project.COLOR_PRESETS

    if request.method == 'POST':
        vertical = None
        if request.POST.get('vertical'):
            vertical = get_object_or_404(Category, id=request.POST.get('vertical'))

        project = Project.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            color_hex=request.POST.get('color_hex', '#534AB7'),
            vertical=vertical,
            status='active',
            created_by=request.user,
        )

        for author_id in request.POST.getlist('members'):
            author = get_object_or_404(Author, id=author_id)
            ProjectMember.objects.get_or_create(project=project, author=author)

        return redirect('/projects')

    return render(request, 'dash/projects/add_project.html', {
        'authors':       authors,
        'categories':    categories,
        'color_presets': color_presets,
    })


@user_passes_test(superadmin_required, login_url='/login_view')
def edit_project(request, id):
    project            = get_object_or_404(Project, id=id)
    authors            = Author.objects.filter(status='Enabled')
    categories         = Category.objects.filter(status='Enabled')
    color_presets      = Project.COLOR_PRESETS
    current_member_ids = list(project.members.values_list('author_id', flat=True))

    if request.method == 'POST':
        project.name        = request.POST.get('name')
        project.description = request.POST.get('description')
        project.color_hex   = request.POST.get('color_hex', project.color_hex)
        vertical_id         = request.POST.get('vertical')
        project.vertical    = get_object_or_404(Category, id=vertical_id) if vertical_id else None
        project.save()

        new_member_ids = request.POST.getlist('members')
        ProjectMember.objects.filter(project=project).exclude(author_id__in=new_member_ids).delete()
        for author_id in new_member_ids:
            author = get_object_or_404(Author, id=author_id)
            ProjectMember.objects.get_or_create(project=project, author=author)

        return redirect('/projects')

    return render(request, 'dash/projects/edit_project.html', {
        'project':            project,
        'authors':            authors,
        'categories':         categories,
        'color_presets':      color_presets,
        'current_member_ids': current_member_ids,
    })


@user_passes_test(superadmin_required, login_url='/login_view')
def project_detail(request, id):
    project = get_object_or_404(Project, id=id)
    tasks   = project.tasks.select_related('assigned_to').prefetch_related(
                'task_articles', 'task_bstvs', 'comments'
              )
    members = project.members.select_related('author')

    board = {
        'todo':       tasks.filter(status='todo').order_by('due_date'),
        'inprogress': tasks.filter(status='inprogress').order_by('due_date'),
        'review':     tasks.filter(status='review').order_by('due_date'),
        'done':       tasks.filter(status='done').order_by('-updated_at'),
    }
    counts = project.task_counts()

    ninety_days_ago = timezone.now() - timedelta(days=90)
    member_stats    = []
    max_actions     = 1

    for membership in members:
        author = membership.author
        logs   = ContributionLog.objects.filter(
                    project=project,
                    author=author,
                    logged_at__gte=ninety_days_ago
                 )
        total  = logs.count()
        stats  = {
            'author':        author,
            'role':          membership.role,
            'total':         total,
            'done':          logs.filter(action='task_done').count(),
            'draft':         logs.filter(action='draft_saved').count(),
            'published':     logs.filter(action='article_published').count(),
            'article_tasks': tasks.filter(assigned_to=author, task_type='article').count(),
            'video_tasks':   tasks.filter(
                                assigned_to=author,
                                task_type__in=['video_shoot','video_edit','video_upload','reel','youtube']
                             ).count(),
            'social_tasks':  tasks.filter(assigned_to=author, task_type='social').count(),
        }
        member_stats.append(stats)
        if total > max_actions:
            max_actions = total

    for s in member_stats:
        s['bar_width'] = round((s['total'] / max_actions) * 100)

    member_stats.sort(key=lambda x: x['total'], reverse=True)

    logs_90    = ContributionLog.objects.filter(
                    project=project,
                    logged_at__gte=ninety_days_ago
                 ).values_list('logged_at', flat=True)
    day_counts = defaultdict(int)
    for dt in logs_90:
        day_counts[dt.date()] += 1

    today   = date.today()
    heatmap = []
    max_day = max(day_counts.values()) if day_counts else 1

    for i in range(89, -1, -1):
        d     = today - timedelta(days=i)
        count = day_counts.get(d, 0)
        if count == 0:                 level = 0
        elif count <= max_day * 0.25:  level = 1
        elif count <= max_day * 0.50:  level = 2
        elif count <= max_day * 0.75:  level = 3
        else:                          level = 4
        heatmap.append({'date': d, 'count': count, 'level': level})

    context = {
        'project':            project,
        'board':              board,
        'counts':             counts,
        'member_stats':       member_stats,
        'heatmap':            heatmap,
        'today':              today,
        'authors':            Author.objects.filter(status='Enabled'),
        'video_types':        ['video_shoot','video_edit','video_upload','reel','youtube'],
        # all tasks for this project — used by both calendars in JS
        'all_project_tasks':  tasks,
        # task type choices for the duplicate modal dropdown
        'task_type_choices':  Task.TYPE_CHOICES,
    }
    return render(request, 'dash/projects/project_detail.html', context)

def archive_project(request, id):
    project = get_object_or_404(Project, id=id)
    project.status = 'archived'
    project.save()
    return redirect('/projects')


def activate_project(request, id):
    project = get_object_or_404(Project, id=id)
    project.status = 'active'
    project.save()
    return redirect('/projects')


def delete_project(request, id):
    project = get_object_or_404(Project, id=id)
    project.delete()
    return redirect('/projects')


# ─────────────────────────────────────────
#  PROJECT MEMBERS
# ─────────────────────────────────────────

def add_project_member(request, project_id):
    project   = get_object_or_404(Project, id=project_id)
    author_id = request.POST.get('author_id')
    role      = request.POST.get('role', 'member')
    if author_id:
        author = get_object_or_404(Author, id=author_id)
        ProjectMember.objects.get_or_create(project=project, author=author, defaults={'role': role})
    return redirect(f'/project_detail/{project_id}')


def remove_project_member(request, project_id, author_id):
    ProjectMember.objects.filter(project_id=project_id, author_id=author_id).delete()
    return redirect(f'/project_detail/{project_id}')


# ─────────────────────────────────────────
#  TASKS
# ─────────────────────────────────────────

@user_passes_test(superadmin_required, login_url='/login_view')
def all_tasks(request):
    tasks = Task.objects.select_related('project', 'assigned_to').order_by('due_date')

    status_filter   = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    project_filter  = request.GET.get('project')

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)

    overdue = tasks.filter(due_date__lt=date.today()).exclude(status='done')

    context = {
        'tasks':    tasks,
        'overdue':  overdue,
        'projects': Project.objects.filter(status='active'),
    }
    return render(request, 'dash/tasks/tasks.html', context)


@user_passes_test(superadmin_required, login_url='/login_view')
def add_task(request, project_id=None):
    projects         = Project.objects.filter(status='active')
    authors          = Author.objects.filter(status='Enabled')
    selected_project = get_object_or_404(Project, id=project_id) if project_id else None

    if request.method == 'POST':
        proj   = get_object_or_404(Project, id=request.POST.get('project'))
        author = None
        if request.POST.get('assigned_to'):
            author = get_object_or_404(Author, id=request.POST.get('assigned_to'))

        task = Task.objects.create(
            title           = request.POST.get('title'),
            description     = request.POST.get('description'),
            project         = proj,
            assigned_to     = author,
            created_by      = request.user,
            status          = request.POST.get('status', 'todo'),
            priority        = request.POST.get('priority', 'medium'),
            task_type       = request.POST.get('task_type', 'general'),
            due_date        = request.POST.get('due_date') or None,
            deploy_date     = request.POST.get('deploy_date') or None,
            deploy_platform = request.POST.get('deploy_platform') or None,
        )

        for art_id in request.POST.getlist('articles'):
            article = get_object_or_404(Article, id=art_id)
            TaskArticle.objects.get_or_create(task=task, article=article)

        for bstv_id in request.POST.getlist('bstvs'):
            bstv = get_object_or_404(BSTV, id=bstv_id)
            TaskBSTV.objects.get_or_create(task=task, bstv=bstv)

        if project_id:
            return redirect(f'/project_detail/{project_id}')
        return redirect('/tasks')

    return render(request, 'dash/tasks/add_task.html', {
        'projects':         projects,
        'authors':          authors,
        'selected_project': selected_project,
        'task_types':       Task.TYPE_CHOICES,
    })


@user_passes_test(superadmin_required, login_url='/login_view')
def edit_task(request, id):
    task                 = get_object_or_404(Task, id=id)
    projects             = Project.objects.filter(status='active')
    authors              = Author.objects.filter(status='Enabled')
    attached_article_ids = list(task.task_articles.values_list('article_id', flat=True))
    attached_bstv_ids    = list(task.task_bstvs.values_list('bstv_id', flat=True))

    if request.method == 'POST':
        task.title           = request.POST.get('title')
        task.description     = request.POST.get('description')
        task.project         = get_object_or_404(Project, id=request.POST.get('project'))
        task.status          = request.POST.get('status', task.status)
        task.priority        = request.POST.get('priority', task.priority)
        task.task_type       = request.POST.get('task_type', task.task_type)
        task.due_date        = request.POST.get('due_date') or None
        task.deploy_date     = request.POST.get('deploy_date') or None
        task.deploy_platform = request.POST.get('deploy_platform') or None

        assigned_id      = request.POST.get('assigned_to')
        task.assigned_to = get_object_or_404(Author, id=assigned_id) if assigned_id else None
        task.save()

        new_article_ids = request.POST.getlist('articles')
        TaskArticle.objects.filter(task=task).exclude(article_id__in=new_article_ids).delete()
        for art_id in new_article_ids:
            TaskArticle.objects.get_or_create(task=task, article=get_object_or_404(Article, id=art_id))

        new_bstv_ids = request.POST.getlist('bstvs')
        TaskBSTV.objects.filter(task=task).exclude(bstv_id__in=new_bstv_ids).delete()
        for bstv_id in new_bstv_ids:
            TaskBSTV.objects.get_or_create(task=task, bstv=get_object_or_404(BSTV, id=bstv_id))

        return redirect(f'/project_detail/{task.project_id}')

    return render(request, 'dash/tasks/edit_task.html', {
        'task':                 task,
        'projects':             projects,
        'authors':              authors,
        'attached_article_ids': attached_article_ids,
        'attached_bstv_ids':    attached_bstv_ids,
        'task_types':           Task.TYPE_CHOICES,
    })


def update_task_status(request, id):
    task       = get_object_or_404(Task, id=id)
    new_status = request.POST.get('status')

    if new_status in dict(Task.STATUS_CHOICES):
        task.status = new_status
        task.save()

        if new_status == 'done' and task.assigned_to:
            ContributionLog.objects.create(
                author=task.assigned_to,
                project=task.project,
                action='task_done',
                task=task,
            )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'new_status': task.get_status_display()})

    return redirect(f'/project_detail/{task.project_id}')


@user_passes_test(superadmin_required, login_url='/login_view')
def duplicate_task(request, id):
    original = get_object_or_404(Task, id=id)

    if request.method == 'POST':
        new_author_id = request.POST.get('assigned_to')
        new_author    = get_object_or_404(Author, id=new_author_id) if new_author_id else None
        new_type      = request.POST.get('task_type', original.task_type)

        clone = Task.objects.create(
            title           = original.title,
            description     = original.description,
            project         = original.project,
            assigned_to     = new_author,
            created_by      = request.user,
            status          = 'todo',
            priority        = original.priority,
            task_type       = new_type,
            due_date        = original.due_date,
            deploy_date     = original.deploy_date,
            deploy_platform = original.deploy_platform,
        )

        if new_type == 'article':
            for ta in original.task_articles.all():
                TaskArticle.objects.get_or_create(task=clone, article=ta.article)

        if new_type in ['video_shoot', 'video_edit', 'video_upload', 'reel', 'youtube', 'social']:
            for tb in original.task_bstvs.all():
                TaskBSTV.objects.get_or_create(task=clone, bstv=tb.bstv)

    return redirect(f'/project_detail/{original.project_id}')


def delete_task(request, id):
    task       = get_object_or_404(Task, id=id)
    project_id = task.project_id
    task.delete()
    return redirect(f'/project_detail/{project_id}')


# ─────────────────────────────────────────
#  TASK ARTICLES
# ─────────────────────────────────────────

def attach_article(request, task_id):
    task       = get_object_or_404(Task, id=task_id)
    article_id = request.POST.get('article_id')
    if article_id:
        article = get_object_or_404(Article, id=article_id)
        TaskArticle.objects.get_or_create(task=task, article=article)
    return redirect(f'/project_detail/{task.project_id}')


def detach_article(request, task_id, article_id):
    TaskArticle.objects.filter(task_id=task_id, article_id=article_id).delete()
    task = get_object_or_404(Task, id=task_id)
    return redirect(f'/project_detail/{task.project_id}')


# ─────────────────────────────────────────
#  TASK COMMENTS
# ─────────────────────────────────────────

@user_passes_test(superadmin_required, login_url='/login_view')
def add_task_comment(request, task_id):
    task   = get_object_or_404(Task, id=task_id)
    body   = request.POST.get('body', '').strip()
    author = getattr(request.user, 'author_profile', None)

    if body and author:
        TaskComment.objects.create(task=task, author=author, body=body)

    return redirect(f'/project_detail/{task.project_id}')


def delete_task_comment(request, id):
    comment    = get_object_or_404(TaskComment, id=id)
    project_id = comment.task.project_id
    comment.delete()
    return redirect(f'/project_detail/{project_id}')


# ─────────────────────────────────────────
#  AJAX
# ─────────────────────────────────────────

def search_articles_for_task(request):
    term     = request.GET.get('term', '')
    articles = Article.objects.filter(title__icontains=term).values('id', 'title')[:20]
    data     = [{'label': a['title'], 'value': a['id']} for a in articles]
    return JsonResponse(data, safe=False)


def search_bstv_for_task(request):
    term  = request.GET.get('term', '').strip()
    items = BSTV.objects.filter(title__icontains=term).values('id', 'title', 'type')[:20]
    data  = [{'label': f"{i['title']} ({i['type']})", 'value': i['id']} for i in items]
    return JsonResponse(data, safe=False)


def heatmap_data(request, project_id):
    project         = get_object_or_404(Project, id=project_id)
    ninety_days_ago = timezone.now() - timedelta(days=90)

    logs = ContributionLog.objects.filter(
        project=project,
        logged_at__gte=ninety_days_ago,
    ).values_list('logged_at', flat=True)

    day_counts = defaultdict(int)
    for dt in logs:
        day_counts[str(dt.date())] += 1

    return JsonResponse(day_counts)