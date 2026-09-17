from django.shortcuts import render,redirect,get_object_or_404
from dash.models import Enquiry,Newsletter,Author,Category,Article,Ad,Tags,BSTV,TrendingArticles,EditorsChoice,TrendingBuzz,Exclusives,ReelsHighlights,Exclusives2,LatestArticles,TheChallengers,Bigshot,Unthink,ArticleFAQ,ArticleHowTo
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

def superadmin_required(user):
    return user.is_superuser 

def login_view(request):
    if request.method == 'POST':  
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')

    return render(request, 'editor/signin.html')

def logout_view(request):
    logout(request)
    return redirect('/login_view')

@user_passes_test(superadmin_required, login_url='/login_view') 
def index(request):
     return render(request,'editor/index.html')


@user_passes_test(superadmin_required, login_url='/login_view') 
def articles(request):
     user = request.user
     author = user.author_profile
     articles = Article.objects.filter(author=author).order_by('-created_at')
     return render(request,'editor/articles/article.html',{'articles':articles})

from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse

def search_articles(request):
    term = request.GET.get('term', '').strip()

    # Safety: user must have an author profile
    if not hasattr(request.user, "author_profile"):
        return JsonResponse([], safe=False)

    author = request.user.author_profile

    articles = (
        Article.objects
        .filter(author=author, title__icontains=term)
        .values('id', 'title')[:20]
    )

    data = [{"label": a["title"], "value": a["id"]} for a in articles]
    return JsonResponse(data, safe=False)

@user_passes_test(superadmin_required, login_url='/login_view') 
def add_article(request):
    categories = Category.objects.all()
    tags = Tags.objects.all()
    author = request.user.author_profile

    if request.method == 'POST':
        # Create Article
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        selected_tag_ids = request.POST.getlist('tags')
        description = request.POST.get('description')
        meta_title = request.POST.get('meta_title')
        meta_description = request.POST.get('meta_description')
        meta_keywords = request.POST.get('meta_keywords')
        content = request.POST.get('content')
        status = request.POST.get('status', 'Enabled')
        
        category = Category.objects.get(id=category_id)

        article = Article.objects.create(
            title=title,
            author=author,
            category=category,
            description=description,
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            content=content,
            status="Disabled",
            title_colour=request.POST.get('title_colour'),
            banner_background_colour=request.POST.get('banner_background_colour'),
            remaining_text_colour=request.POST.get('remaining_text_colour'),
            banner_image=request.FILES.get('banner_image'),
            thumbnail_image=request.FILES.get('thumbnail_image'),
        )

        # Tags
        article.tags.set(selected_tag_ids)

        # ------------------------
        # SAVE FAQ ENTRIES
        # ------------------------
        faq_indexes = request.POST.getlist("faq_index")

        for index in faq_indexes:
            q = request.POST.get(f"faq_question_{index}")
            a = request.POST.get(f"faq_answer_{index}")
            if q and a:
                ArticleFAQ.objects.create(
                    article=article,
                    question=q,
                    answer=a
                )

        # ------------------------
        # SAVE HOWTO STEPS
        # ------------------------
        howto_indexes = request.POST.getlist("howto_index")

        for index in howto_indexes:
            name = request.POST.get(f"howto_name_{index}")
            text = request.POST.get(f"howto_text_{index}")

            if name and text:
                ArticleHowTo.objects.create(
                    article=article,
                    step_name=name,
                    step_text=text
                )

        return redirect('/articles')

    return render(request, 'editor/articles/add_article.html', {
        
        'categories': categories,
        'tags': tags
    })


from django.conf import settings
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt
def upload_quill_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        image_name = image.name
        save_path = os.path.join(settings.MEDIA_ROOT, 'quill_uploads', image_name)

        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        image_url = settings.MEDIA_URL + 'quill_uploads/' + image_name
        return JsonResponse({'url': image_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@user_passes_test(superadmin_required, login_url='/login_view') 
def edit_article(request, id):
    categories = Category.objects.all()
    tags = Tags.objects.all()
    data = get_object_or_404(Article, id=id)

    if request.method == 'POST':
        # Update article main fields...
        data.title = request.POST.get('title')
        data.description = request.POST.get('description')
        data.meta_title = request.POST.get('meta_title')
        data.meta_description = request.POST.get('meta_description')
        data.meta_keywords = request.POST.get('meta_keywords')
        data.content = request.POST.get('content')
        data.status = request.POST.get('status', 'Enabled') 

        data.author = request.user.author_profile
        data.category = Category.objects.get(id=request.POST.get('category'))

        selected_tag_ids = request.POST.getlist('tags')
        data.tags.set(selected_tag_ids)

        # Save images only if new uploaded
        if request.FILES.get('banner_image'):
            data.banner_image = request.FILES.get('banner_image')

        if request.FILES.get('thumbnail_image'):
            data.thumbnail_image = request.FILES.get('thumbnail_image')

        data.save()

        # ==============================
        # UPDATE EXISTING FAQS
        # ==============================
        for faq in data.faqs.all():
            if request.POST.get(f"faq_delete_{faq.id}"):
                faq.delete()
                continue

            faq.question = request.POST.get(f"faq_question_existing_{faq.id}")
            faq.answer = request.POST.get(f"faq_answer_existing_{faq.id}")
            faq.save()

        # ADD NEW FAQS
        new_faq_indexes = request.POST.getlist("faq_new_index")
        for index in new_faq_indexes:
            q = request.POST.get(f"faq_question_new_{index}")
            a = request.POST.get(f"faq_answer_new_{index}")
            if q and a:
                ArticleFAQ.objects.create(article=data, question=q, answer=a)

        # ==============================
        # UPDATE EXISTING HOWTO STEPS
        # ==============================
        for step in data.howto_steps.all():
            if request.POST.get(f"howto_delete_{step.id}"):
                step.delete()
                continue

            step.step_name = request.POST.get(f"howto_name_existing_{step.id}")
            step.step_text = request.POST.get(f"howto_text_existing_{step.id}")
            step.save()

        # ADD NEW HOWTO STEPS
        new_step_indexes = request.POST.getlist("howto_new_index")
        for index in new_step_indexes:
            name = request.POST.get(f"howto_name_new_{index}")
            text = request.POST.get(f"howto_text_new_{index}")
            if name and text:
                ArticleHowTo.objects.create(article=data, step_name=name, step_text=text)

        return redirect('/articles')

    return render(request, 'editor/articles/edit_article.html', {
        
        'categories': categories,
        'tags': tags,
        'data': data
    })

def custom_error_handler(request, status_code, exception=None):
    return render(request, 'editor/error.html', {'status_code': status_code, 'message': exception}, status=status_code)

def custom_404(request, exception):
    return custom_error_handler(request, 404, exception)

def custom_500(request):
    return custom_error_handler(request, 500)

def custom_403(request, exception):
    return custom_error_handler(request, 403, exception)

def custom_400(request, exception):
    return custom_error_handler(request, 400, exception)


@user_passes_test(superadmin_required, login_url='/login_view') 
def profile(request):
     profile = request.user.author_profile
     return render(request,'editor/editors/profile.html',{'profile':profile})

@user_passes_test(superadmin_required, login_url='/login_view') 
def edit_editor(request):
     data = request.user.author_profile
     if request.method == 'POST':
        data.name = request.POST.get('name')
        data.designation = request.POST.get('designation')
        data.description = request.POST.get('description')
        data.email = request.POST.get('email')
        data.DOB = request.POST.get('DOB')
        data.location = request.POST.get('location')
        data.image = request.FILES.get('image')
        data.facebook_url = request.POST.get('facebook_url')
        data.instagram_url = request.POST.get('instagram_url')
        data.linkedin_url = request.POST.get('linkedin_url')
        data.twitter_url = request.POST.get('twitter_url')
        data.save()
        return redirect('/profile')
     
     return render(request,'editor/editors/edit_editors.html',{'data':data})