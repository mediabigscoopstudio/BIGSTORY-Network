from django.urls import path
from content import views
from content import task_views
from django.conf import settings
from django.conf.urls.static import static

handler400 = views.custom_400
handler403 = views.custom_403
handler404 = views.custom_404
handler500 = views.custom_500

urlpatterns = [

    # ─────────────────────────────────────────
    #  CORE
    # ─────────────────────────────────────────
    path("",             task_views.index,    name='index'),
    path("login_view",   views.login_view,    name='login_view'),
    path("logout_view",  views.logout_view,   name='logout_view'),

    # ─────────────────────────────────────────
    #  PROFILE
    # ─────────────────────────────────────────
    path("profile",      views.profile,       name='profile'),
    path("edit_profile", views.edit_editor,   name='edit_profile'),

    # ─────────────────────────────────────────
    #  BSTV
    # ─────────────────────────────────────────
    path("bstv",                views.bstv,         name='bstv'),
    path("add_bstv",            views.add_bstv,      name='add_bstv'),
    path("edit_bstv/<id>",      views.edit_bstv,     name='edit_bstv'),
    path("ajax/search_bstv/",   views.search_bstv,   name='search_bstv'),

    # ─────────────────────────────────────────
    #  PROJECTS
    # ─────────────────────────────────────────
    path("my_projects",                task_views.my_projects,    name='my_projects'),
    path("project_tasks/<project_id>", task_views.project_tasks,  name='project_tasks'),

    # ─────────────────────────────────────────
    #  TASKS
    # ─────────────────────────────────────────
    path("my_tasks",                   task_views.my_tasks,           name='my_tasks'),
    path("add_task",                   task_views.add_task,           name='add_task'),
    path("add_task/<project_id>",      task_views.add_task,           name='add_task_project'),
    path("task_detail/<id>",           task_views.task_detail,        name='task_detail'),
    path("update_task_status/<id>",    task_views.update_task_status, name='update_task_status'),

    # ─────────────────────────────────────────
    #  CALENDAR
    # ─────────────────────────────────────────
    path("calendar",                   task_views.content_calendar,   name='calendar'),

    # ─────────────────────────────────────────
    #  BSTV ATTACH / DETACH ON TASKS
    # ─────────────────────────────────────────
    path("attach_bstv/<task_id>",              task_views.attach_bstv,     name='attach_bstv'),
    path("detach_bstv/<task_id>/<bstv_id>",    task_views.detach_bstv,     name='detach_bstv'),

    # ─────────────────────────────────────────
    #  COMMENTS
    # ─────────────────────────────────────────
    path("add_task_comment/<task_id>", task_views.add_task_comment,   name='add_task_comment'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)