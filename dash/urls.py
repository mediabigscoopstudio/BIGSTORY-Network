from django.contrib import admin
from django.urls import path
from dash import views
from dash.tasks import task_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

handler400 = views.custom_400
handler403 = views.custom_403
handler404 = views.custom_404
handler500 = views.custom_500

urlpatterns = [

    # ─────────────────────────────────────────
    #  CORE
    # ─────────────────────────────────────────
    path("",          task_views.index,       name='index'),   # dashboard with task manager
    path("admin/",    admin.site.urls),
    path("login_view",  views.login_view,     name='login_view'),
    path("logout_view", views.logout_view,    name='logout_view'),

    # ─────────────────────────────────────────
    #  ENQUIRY
    # ─────────────────────────────────────────
    path("enquiry",                 views.enquiry,          name='enquiry'),
    path("view_details/<id>",       views.view_details,     name='view_details'),
    path("resolve_enquiry/<id>",    views.resolve_enquiry,  name='resolve_enquiry'),

    # ─────────────────────────────────────────
    #  EDITORS  (Authors as staff)
    # ─────────────────────────────────────────
    path("editors",                 views.editors,          name='editors'),
    path("editor_details/<id>",     views.editor_details,   name='editor_details'),
    path("add_editor",              views.add_editor,       name='add_editor'),
    path("disable_editor/<id>",     views.disable_editor,   name='disable_editor'),
    path("enable_editor/<id>",      views.enable_editor,    name='enable_editor'),
    path("delete_editor/<id>",      views.delete_editor,    name='delete_editor'),
    path("edit_editor/<id>",        views.edit_editor,      name='edit_editor'),
    path("profile/<id>",            views.profile,          name='profile'),

    # ─────────────────────────────────────────
    #  CATEGORIES
    # ─────────────────────────────────────────
    path("categories",              views.categories,       name='categories'),
    path("add_category",            views.add_category,     name='add_category'),
    path("disable_category/<id>",   views.disable_category, name='disable_category'),
    path("enable_category/<id>",    views.enable_category,  name='enable_category'),
    path("delete_category/<id>",    views.delete_category,  name='delete_category'),
    path("edit_category/<id>",      views.edit_category,    name='edit_category'),

    # ─────────────────────────────────────────
    #  TAGS
    # ─────────────────────────────────────────
    path("tags",                    views.tags,             name='tags'),
    path("add_tags",                views.add_tags,         name='add_tags'),
    path("disable_tags/<id>",       views.disable_tags,     name='disable_tags'),
    path("enable_tags/<id>",        views.enable_tags,      name='enable_tags'),
    path("delete_tags/<id>",        views.delete_tags,      name='delete_tags'),
    path("edit_tags/<id>",          views.edit_tags,        name='edit_tags'),

    # ─────────────────────────────────────────
    #  ARTICLES
    # ─────────────────────────────────────────
    path("articles",                        views.articles,             name='articles'),
    path('ajax/search_articles/',           views.search_articles,      name='search_articles'),
    path('upload_quill_image/',             views.upload_quill_image,   name='upload_quill_image'),
    path("add_article",                     views.add_article,          name='add_article'),
    path("disable_article/<id>",            views.disable_article,      name='disable_article'),
    path("enable_article/<id>",             views.enable_article,       name='enable_article'),
    path("delete_article/<id>",             views.delete_article,       name='delete_article'),
    path("edit_article/<id>",               views.edit_article,         name='edit_article'),

    # ─────────────────────────────────────────
    #  BSTV
    # ─────────────────────────────────────────
    path("bstv",                    views.bstv,             name='bstv'),
    path("add_bstv",                views.add_bstv,         name='add_bstv'),
    path("disable_bstv/<id>",       views.disable_bstv,     name='disable_bstv'),
    path("enable_bstv/<id>",        views.enable_bstv,      name='enable_bstv'),
    path("delete_bstv/<id>",        views.delete_bstv,      name='delete_bstv'),
    path("edit_bstv/<id>",          views.edit_bstv,        name='edit_bstv'),

    # ─────────────────────────────────────────
    #  CONTENT MANAGEMENT
    # ─────────────────────────────────────────
    path("content_management",          views.content_management,       name='content_management'),
    path("trending_articles",           views.trending_articles,        name='trending_articles'),
    path("update_editors_choice",       views.update_editors_choice,    name='update_editors_choice'),
    path("update_trending_buzz",        views.update_trending_buzz,     name='update_trending_buzz'),
    path("update_exclusives",           views.update_exclusives,        name='update_exclusives'),
    path("update_exclusives2",          views.update_exclusives2,       name='update_exclusives2'),
    path("update_latest_articles",      views.update_latest_articles,   name='update_latest_articles'),
    path("update_reel_highlights",      views.update_reel_highlights,   name='update_reel_highlights'),
    path("update_the_challengers",      views.update_the_challengers,   name='update_the_challengers'),
    path("update_bigshot",              views.update_bigshot,           name='update_bigshot'),
    path("update_unthink",              views.update_unthink,           name='update_unthink'),

    # ─────────────────────────────────────────
    #  TASK MANAGER — PROJECTS
    # ─────────────────────────────────────────
    path("projects",                            task_views.projects,            name='projects'),
    path("add_project",                         task_views.add_project,         name='add_project'),
    path("edit_project/<id>",                   task_views.edit_project,        name='edit_project'),
    path("project_detail/<id>",                 task_views.project_detail,      name='project_detail'),
    path("archive_project/<id>",                task_views.archive_project,     name='archive_project'),
    path("activate_project/<id>",               task_views.activate_project,    name='activate_project'),
    path("delete_project/<id>",                 task_views.delete_project,      name='delete_project'),
     path("duplicate_task/<id>",             task_views.duplicate_task,           name='duplicate_task'),
 
    # BSTV search for task forms in dash
    path("ajax/search_bstv_for_task/",      task_views.search_bstv_for_task,     name='search_bstv_for_task'),
 

    # ─────────────────────────────────────────
    #  TASK MANAGER — PROJECT MEMBERS
    # ─────────────────────────────────────────
    path("add_project_member/<project_id>",             task_views.add_project_member,    name='add_project_member'),
    path("remove_project_member/<project_id>/<author_id>", task_views.remove_project_member, name='remove_project_member'),

    # ─────────────────────────────────────────
    #  TASK MANAGER — TASKS
    # ─────────────────────────────────────────
    path("tasks",                               task_views.all_tasks,           name='all_tasks'),
    path("add_task",                            task_views.add_task,            name='add_task'),
    path("add_task/<project_id>",               task_views.add_task,            name='add_task_for_project'),
    path("edit_task/<id>",                      task_views.edit_task,           name='edit_task'),
    path("update_task_status/<id>",             task_views.update_task_status,  name='update_task_status'),
    path("delete_task/<id>",                    task_views.delete_task,         name='delete_task'),

    # ─────────────────────────────────────────
    #  TASK MANAGER — ARTICLES ON TASKS
    # ─────────────────────────────────────────
    path("attach_article/<task_id>",                    task_views.attach_article,  name='attach_article'),
    path("detach_article/<task_id>/<article_id>",       task_views.detach_article,  name='detach_article'),
    path("ajax/search_articles_for_task/",              task_views.search_articles_for_task, name='search_articles_for_task'),

    # ─────────────────────────────────────────
    #  TASK MANAGER — COMMENTS
    # ─────────────────────────────────────────
    path("add_task_comment/<task_id>",      task_views.add_task_comment,    name='add_task_comment'),
    path("delete_task_comment/<id>",        task_views.delete_task_comment, name='delete_task_comment'),

    # ─────────────────────────────────────────
    #  TASK MANAGER — HEATMAP API
    # ─────────────────────────────────────────
    path("ajax/heatmap/<project_id>",       task_views.heatmap_data,        name='heatmap_data'),
    
    # ─────────────────────────────────────────
    #  ANALYTICS
    # ─────────────────────────────────────────

    path("analytics", views.analytics_dashboard, name='analytics'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)