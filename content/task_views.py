from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from collections import defaultdict
import calendar as cal

from dash.models import (
    Author, BSTV, Category,
    
)
from dash.tasks.task_models import (Project, ProjectMember, Task, TaskBSTV, TaskComment, ContributionLog)

# ─────────────────────────────────────────
#  Auth guard
# ─────────────────────────────────────────

def get_author_or_redirect(request):
    if not request.user.is_authenticated:
        return None
    try:
        return request.user.author_profile
    except Exception:
        return None


# ─────────────────────────────────────────
#  VIDEO / SOCIAL task types for content team
# ─────────────────────────────────────────

CONTENT_TASK_TYPES = [
    ('video_shoot',  'Video — Shoot'),
    ('video_edit',   'Video — Edit'),
    ('video_upload', 'Video — Upload'),
    ('reel',         'Reel'),
    ('youtube',      'YouTube'),
    ('social',       'Social Media'),
    ('calendar',     'Content Calendar'),
    ('general',      'General'),
]


# ─────────────────────────────────────────
#  DASHBOARD INDEX
# ─────────────────────────────────────────

def index(request):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    today    = date.today()
    my_tasks = Task.objects.filter(assigned_to=author).select_related('project')

    task_summary = {
        'total':      my_tasks.count(),
        'todo':       my_tasks.filter(status='todo').count(),
        'inprogress': my_tasks.filter(status='inprogress').count(),
        'review':     my_tasks.filter(status='review').count(),
        'done':       my_tasks.filter(status='done').count(),
        'overdue':    my_tasks.filter(due_date__lt=today).exclude(status='done').count(),
    }

    overdue_tasks = my_tasks.filter(due_date__lt=today).exclude(status='done').order_by('due_date')
    recent_tasks  = my_tasks.exclude(status='done').order_by('due_date')[:8]
    my_projects   = Project.objects.filter(
                        members__author=author,
                        status='active'
                    ).distinct()

    # upcoming tasks this week
    week_end      = today + timedelta(days=7)
    upcoming      = my_tasks.filter(
                        due_date__gte=today,
                        due_date__lte=week_end
                    ).exclude(status='done').order_by('due_date')

    # 90-day personal heatmap
    ninety_days_ago = timezone.now() - timedelta(days=90)
    logs = ContributionLog.objects.filter(
        author=author,
        logged_at__gte=ninety_days_ago
    ).values_list('logged_at', flat=True)

    day_counts = defaultdict(int)
    for dt in logs:
        day_counts[dt.date()] += 1

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
        'author':       author,
        'task_summary': task_summary,
        'overdue_tasks': overdue_tasks,
        'recent_tasks': recent_tasks,
        'upcoming':     upcoming,
        'my_projects':  my_projects,
        'heatmap':      heatmap,
        'today':        today,
    }
    return render(request, 'content/index.html', context)


# ─────────────────────────────────────────
#  MY PROJECTS — read-only overview
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
        my_counts = {
            'todo':       Task.objects.filter(project=p, assigned_to=author, status='todo').count(),
            'inprogress': Task.objects.filter(project=p, assigned_to=author, status='inprogress').count(),
            'review':     Task.objects.filter(project=p, assigned_to=author, status='review').count(),
            'done':       Task.objects.filter(project=p, assigned_to=author, status='done').count(),
            'overdue':    Task.objects.filter(project=p, assigned_to=author, due_date__lt=date.today()).exclude(status='done').count(),
        }
        projects_data.append({
            'project':   p,
            'role':      m.role,
            'my_counts': my_counts,
        })

    return render(request, 'content/tasks/my_projects.html', {
        'author':        author,
        'projects_data': projects_data,
    })


# ─────────────────────────────────────────
#  MY TASKS — full list with filters
# ─────────────────────────────────────────

def my_tasks(request):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    tasks = Task.objects.filter(assigned_to=author).select_related('project').order_by('due_date')

    status_filter  = request.GET.get('status')
    project_filter = request.GET.get('project')
    type_filter    = request.GET.get('task_type')

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)
    if type_filter:
        tasks = tasks.filter(task_type=type_filter)

    today       = date.today()
    overdue     = tasks.filter(due_date__lt=today).exclude(status='done')
    my_projects = Project.objects.filter(members__author=author, status='active').distinct()

    return render(request, 'content/tasks/my_tasks.html', {
        'author':           author,
        'tasks':            tasks,
        'overdue':          overdue,
        'my_projects':      my_projects,
        'content_types':    CONTENT_TASK_TYPES,
        'today':            today,
    })


# ─────────────────────────────────────────
#  ADD TASK — content team creates tasks
# ─────────────────────────────────────────

def add_task(request, project_id=None):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    # content team can only create tasks in projects they're a member of
    my_projects      = Project.objects.filter(members__author=author, status='active').distinct()
    selected_project = get_object_or_404(Project, id=project_id) if project_id else None

    if request.method == 'POST':
        project = get_object_or_404(Project, id=request.POST.get('project'))

        # verify author is a member of this project
        if not ProjectMember.objects.filter(project=project, author=author).exists():
            return redirect('/my_projects')

        task = Task.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            project=project,
            assigned_to=author,          # always assigned to themselves
            created_by=request.user,
            status=request.POST.get('status', 'todo'),
            priority=request.POST.get('priority', 'medium'),
            task_type=request.POST.get('task_type', 'general'),
            due_date=request.POST.get('due_date') or None,
        )

        # attach BSTV videos
        for bstv_id in request.POST.getlist('bstvs'):
            bstv = get_object_or_404(BSTV, id=bstv_id)
            TaskBSTV.objects.get_or_create(task=task, bstv=bstv)

        # log contribution
        ContributionLog.objects.create(
            author=author,
            project=project,
            action='draft_saved',
        )

        if project_id:
            return redirect(f'/project_tasks/{project_id}')
        return redirect('/my_tasks')

    return render(request, 'content/tasks/add_task.html', {
        'author':           author,
        'my_projects':      my_projects,
        'selected_project': selected_project,
        'content_types':    CONTENT_TASK_TYPES,
        'priorities':       Task.PRIORITY_CHOICES,
    })


# ─────────────────────────────────────────
#  TASK DETAIL — view + comment + attach BSTV
# ─────────────────────────────────────────

def task_detail(request, id):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    task     = get_object_or_404(Task, id=id, assigned_to=author)
    bstvs    = task.task_bstvs.select_related('bstv')
    comments = task.comments.select_related('author').order_by('created_at')

    return render(request, 'content/tasks/task_detail.html', {
        'author':   author,
        'task':     task,
        'bstvs':    bstvs,
        'comments': comments,
    })


# ─────────────────────────────────────────
#  UPDATE TASK STATUS
#  Content team: todo → inprogress → review only
# ─────────────────────────────────────────

def update_task_status(request, id):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    task       = get_object_or_404(Task, id=id, assigned_to=author)
    new_status = request.POST.get('status')
    ALLOWED    = ['todo', 'inprogress', 'review']

    if request.method == 'POST' and new_status in ALLOWED:
        task.status = new_status
        task.save()

    # redirect back to wherever they came from
    next_url = request.POST.get('next', '/my_tasks')
    return redirect(next_url)


# ─────────────────────────────────────────
#  PROJECT TASKS — tasks inside one project
# ─────────────────────────────────────────

def project_tasks(request, project_id):
    author  = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    project = get_object_or_404(Project, id=project_id)

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

    return render(request, 'content/tasks/project_tasks.html', {
        'author':    author,
        'project':   project,
        'board':     board,
        'my_counts': my_counts,
        'today':     date.today(),
    })


# ─────────────────────────────────────────
#  CONTENT CALENDAR — monthly task grid
# ─────────────────────────────────────────

def content_calendar(request):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    today = date.today()

    # month/year from GET params, default to current month
    try:
        year  = int(request.GET.get('year',  today.year))
        month = int(request.GET.get('month', today.month))
    except ValueError:
        year, month = today.year, today.month

    # clamp to valid range
    if month < 1:  month = 12; year -= 1
    if month > 12: month = 1;  year += 1

    # all tasks for this author with a due_date in this month
    tasks_this_month = Task.objects.filter(
        assigned_to=author,
        due_date__year=year,
        due_date__month=month,
    ).select_related('project').order_by('due_date')

    # group tasks by day number
    tasks_by_day = defaultdict(list)
    for task in tasks_this_month:
        tasks_by_day[task.due_date.day].append(task)

    # build calendar weeks — list of weeks, each week is list of day dicts
    _, num_days = cal.monthrange(year, month)
    first_weekday = cal.monthrange(year, month)[0]  # 0=Mon

    weeks   = []
    week    = []
    day_num = 1

    # leading empty cells
    for _ in range(first_weekday):
        week.append(None)

    for day_num in range(1, num_days + 1):
        week.append({
            'day':    day_num,
            'date':   date(year, month, day_num),
            'tasks':  tasks_by_day.get(day_num, []),
            'is_today': date(year, month, day_num) == today,
        })
        if len(week) == 7:
            weeks.append(week)
            week = []

    # trailing empty cells
    while len(week) < 7 and week:
        week.append(None)
    if week:
        weeks.append(week)

    # prev / next month navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year  = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year  = year if month < 12 else year + 1

    return render(request, 'content/tasks/calendar.html', {
        'author':        author,
        'weeks':         weeks,
        'year':          year,
        'month':         month,
        'month_name':    cal.month_name[month],
        'prev_year':     prev_year,
        'prev_month':    prev_month,
        'next_year':     next_year,
        'next_month':    next_month,
        'today':         today,
        'total_tasks':   tasks_this_month.count(),
    })


# ─────────────────────────────────────────
#  ATTACH / DETACH BSTV on a task
# ─────────────────────────────────────────

def attach_bstv(request, task_id):
    author  = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    task    = get_object_or_404(Task, id=task_id, assigned_to=author)
    bstv_id = request.POST.get('bstv_id')

    if bstv_id:
        bstv = get_object_or_404(BSTV, id=bstv_id)
        TaskBSTV.objects.get_or_create(task=task, bstv=bstv)

    return redirect(f'/task_detail/{task_id}')


def detach_bstv(request, task_id, bstv_id):
    author = get_author_or_redirect(request)
    if not author:
        return redirect('/login_view')

    task = get_object_or_404(Task, id=task_id, assigned_to=author)
    TaskBSTV.objects.filter(task=task, bstv_id=bstv_id).delete()
    return redirect(f'/task_detail/{task_id}')


# ─────────────────────────────────────────
#  COMMENTS
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
#  AJAX — BSTV search for task attach
# ─────────────────────────────────────────

def search_bstv(request):
    term  = request.GET.get('term', '').strip()
    items = BSTV.objects.filter(
        title__icontains=term,
        status='Enabled'
    ).values('id', 'title', 'type', 'category')[:20]
    data = [{'label': f"{i['title']} ({i['type']})", 'value': i['id']} for i in items]
    return JsonResponse(data, safe=False)