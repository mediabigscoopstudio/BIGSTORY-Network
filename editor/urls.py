from django.contrib import admin
from django.urls import path
from editor import views
from editor import task_views
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
    path("",             task_views.index,       name='index'),   # overrides old blank index
    path("login_view",   views.login_view,       name='login_view'),
    path("logout_view",  views.logout_view,      name='logout_view'),

    # ─────────────────────────────────────────
    #  ARTICLES  (existing)
    # ─────────────────────────────────────────
    path("articles",                        views.articles,         name='articles'),
    path('ajax/search_articles/',           views.search_articles,  name='search_articles'),
    path('upload_quill_image/',             views.upload_quill_image, name='upload_quill_image'),
    path("add_article",                     views.add_article,      name='add_article'),
    path("edit_article/<id>",               views.edit_article,     name='edit_article'),

    # ─────────────────────────────────────────
    #  PROFILE  (existing)
    # ─────────────────────────────────────────
    path("profile",      views.profile,          name='profile'),
    path("edit_editor",  views.edit_editor,      name='edit_editor'),

    # ─────────────────────────────────────────
    #  TASK MANAGER — PROJECTS (read-only)
    # ─────────────────────────────────────────
    path("my_projects",                 task_views.my_projects,     name='my_projects'),
    path("project_tasks/<project_id>",  task_views.project_tasks,   name='project_tasks'),

    # ─────────────────────────────────────────
    #  TASK MANAGER — TASKS
    # ─────────────────────────────────────────
    path("my_tasks",                        task_views.my_tasks,            name='my_tasks'),
    path("task_detail/<id>",                task_views.task_detail,         name='task_detail'),
    path("update_task_status/<id>",         task_views.update_task_status,  name='update_task_status'),

    # ─────────────────────────────────────────
    #  TASK MANAGER — COMMENTS
    # ─────────────────────────────────────────
    path("add_task_comment/<task_id>",      task_views.add_task_comment,    name='add_task_comment'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)