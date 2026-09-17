from django.contrib import admin
from .models import UserProfile, Category, Author, Article, Newsletter, Ad, Enquiry, Tags,BSTV,AboutPageTeams
# Register your models here.
from .models import LatestArticles,Exclusives2,ReelsHighlights,Exclusives,TrendingBuzz,EditorsChoice,TrendingArticles,TheChallengers,Unthink,Bigshot,WriterApplication,ArticleFAQ,ArticleHowTo
# Home Section Dashboard
from dash.tasks.task_models import (Project,ProjectMember,Task,TaskArticle,TaskComment,ContributionLog,)
# Task Management Section Dashboard
from dash.green_india_models import GreenIndiaLead
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Article)
admin.site.register(Newsletter)
admin.site.register(Ad)
admin.site.register(Enquiry)
admin.site.register(Tags)
admin.site.register(BSTV)
admin.site.register(AboutPageTeams)

admin.site.register(LatestArticles)
admin.site.register(Exclusives2)
admin.site.register(ReelsHighlights)
admin.site.register(Exclusives)
admin.site.register(TrendingBuzz)
admin.site.register(EditorsChoice)
admin.site.register(TrendingArticles)

admin.site.register(TheChallengers)
admin.site.register(Bigshot)
admin.site.register(Unthink)
admin.site.register(WriterApplication)

admin.site.register(ArticleHowTo)
admin.site.register(ArticleFAQ)

admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(Task)
admin.site.register(TaskArticle)
admin.site.register(TaskComment)
admin.site.register(ContributionLog)


admin.site.register(GreenIndiaLead)