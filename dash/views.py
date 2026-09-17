from django.shortcuts import render,redirect,get_object_or_404
from .models import Enquiry,Newsletter,Author,Category,Article,Ad,Tags,BSTV,TrendingArticles,EditorsChoice,TrendingBuzz,Exclusives,ReelsHighlights,Exclusives2,LatestArticles,TheChallengers,Bigshot,Unthink,ArticleFAQ,ArticleHowTo
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

    return render(request, 'dash/signin.html')

def logout_view(request):
    logout(request)
    return redirect('/login_view')


@user_passes_test(superadmin_required, login_url='/login_view') 
def index(request):
     return render(request,'dash/index.html')

@user_passes_test(superadmin_required, login_url='/login_view') 
def news_letters(request):
     subscribers = Newsletter.objects.all()
     return render(request,'dash/subscribers/newsletters.html',{'subscribers':subscribers})

@user_passes_test(superadmin_required, login_url='/login_view') 
def enquiry(request):
     enquiries = Enquiry.objects.all()
     return render(request,'dash/enquiry/enquiries.html',{'enquiries':enquiries})

@user_passes_test(superadmin_required, login_url='/login_view') 
def view_details(request,id):
     data = get_object_or_404(Enquiry,id=id)
     return render(request,'dash/enquiry/view_details.html',{'data':data})


def resolve_enquiry(request,id):
     data = get_object_or_404(Enquiry,id=id)
     data.status = "Resolved"
     data.save()
     return redirect('/enquiry')

@user_passes_test(superadmin_required, login_url='/login_view') 
def editors(request):
     editors = Author.objects.all()
     return render(request,'dash/editors/editors.html',{'editors':editors})

@user_passes_test(superadmin_required, login_url='/login_view') 
def editor_details(request,id):
     data = get_object_or_404(Author,id=id)
     return render(request,'dash/editors/editor_details.html',{'data':data})

@user_passes_test(superadmin_required, login_url='/login_view') 
def profile(request,id):
     profile = get_object_or_404(Author,id=id)
     return render(request,'dash/editors/profile.html',{'profile':profile})

@user_passes_test(superadmin_required, login_url='/login_view')
def add_editor(request):
    if request.method == 'POST':
        # USER DATA
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        # AUTHOR DATA
        name = request.POST.get('name')
        designation = request.POST.get('designation')
        description = request.POST.get('description')
        DOB = request.POST.get('DOB') or None
        location = request.POST.get('location')
        image = request.FILES.get('image')
        facebook_url = request.POST.get('facebook_url')
        instagram_url = request.POST.get('instagram_url')
        linkedin_url = request.POST.get('linkedin_url')
        twitter_url = request.POST.get('twitter_url')
        status = "Enabled"

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('/editors/add')

        # CREATE USER (ACTIVE)
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_superuser=True,
        )

        # CREATE AUTHOR
        Author.objects.create(
            user=user,
            name=name,
            designation=designation,
            description=description,
            email=email,
            DOB=DOB,
            location=location,
            image=image,
            facebook_url=facebook_url,
            instagram_url=instagram_url,
            linkedin_url=linkedin_url,
            twitter_url=twitter_url,
            status=status
        )

        messages.success(request, 'Editor registered successfully and activated.')
        return redirect('/editors')

    return render(request, 'dash/editors/add_editor.html')

@user_passes_test(superadmin_required, login_url='/login_view') 
def edit_editor(request,id):
     data = get_object_or_404(Author,id=id)
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
        return redirect('/editors')
     
     return render(request,'dash/editors/edit_editors.html',{'data':data})

def disable_editor(request,id):
     data = get_object_or_404(Author,id=id)
     data.status = "Disabled"
     data.save()
     return redirect('/editors')

def enable_editor(request,id):
     data = get_object_or_404(Author,id=id)
     data.status = "Enabled"
     data.save()
     return redirect('/editors')

def delete_editor(request,id):
     data = get_object_or_404(Author,id=id)
     data.delete()
     return redirect('/editors')

@user_passes_test(superadmin_required, login_url='/login_view') 
def categories(request):
     categories = Category.objects.all()
     return render(request,'dash/category/categories.html',{'categories':categories})

@user_passes_test(superadmin_required, login_url='/login_view') 
def add_category(request):
     if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        meta_title = request.POST.get('meta_title')
        meta_description = request.POST.get('meta_description')
        meta_keywords = request.POST.get('meta_keywords')

        Category.objects.create(
                title=title,
                description=description,
                meta_title=meta_title,
                meta_description=meta_description,
                meta_keywords=meta_keywords,
            )
        return redirect('/categories') 

     return render(request, 'dash/category/add_category.html') 


def disable_category(request,id):
     data = get_object_or_404(Category,id=id)
     data.status = "Disabled"
     data.save()
     return redirect('/categories')

def enable_category(request,id):
     data = get_object_or_404(Category,id=id)
     data.status = "Enabled"
     data.save()
     return redirect('/categories')

def delete_category(request,id):
     data = get_object_or_404(Category,id=id)
     data.delete()
     return redirect('/categories')

@user_passes_test(superadmin_required, login_url='/login_view') 
def edit_category(request,id):
     data = get_object_or_404(Category,id=id)
     if request.method == 'POST':
        data.title = request.POST.get('title')
        data.description = request.POST.get('description')
        data.meta_title = request.POST.get('meta_title')
        data.meta_description = request.POST.get('meta_description')
        data.meta_keywords = request.POST.get('meta_keywords')
        data.save()
        return redirect('/categories') 

     return render(request, 'dash/category/edit_category.html',{'data':data}) 

@user_passes_test(superadmin_required, login_url='/login_view') 
def tags(request):
     tags = Tags.objects.all()
     return render(request,'dash/tags/tags.html',{'tags':tags})

@user_passes_test(superadmin_required, login_url='/login_view') 
def add_tags(request):
     if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        meta_title = request.POST.get('meta_title')
        meta_description = request.POST.get('meta_description')
        meta_keywords = request.POST.get('meta_keywords')

        Tags.objects.create(
                title=title,
                description=description,
                meta_title=meta_title,
                meta_description=meta_description,
                meta_keywords=meta_keywords,
            )
        return redirect('/tags') 

     return render(request, 'dash/tags/add_tags.html') 


def disable_tags(request,id):
     data = get_object_or_404(Tags,id=id)
     data.status = "Disabled"
     data.save()
     return redirect('/tags')

def enable_tags(request,id):
     data = get_object_or_404(Tags,id=id)
     data.status = "Enabled"
     data.save()
     return redirect('/tags')

def delete_tags(request,id):
     data = get_object_or_404(Tags,id=id)
     data.delete()
     return redirect('/tags')

@user_passes_test(superadmin_required, login_url='/login_view') 
def edit_tags(request,id):
     data = get_object_or_404(Tags,id=id)
     if request.method == 'POST':
        data.title = request.POST.get('title')
        data.description = request.POST.get('description')
        data.meta_title = request.POST.get('meta_title')
        data.meta_description = request.POST.get('meta_description')
        data.meta_keywords = request.POST.get('meta_keywords')
        data.save()
        return redirect('/tags') 

     return render(request, 'dash/tags/edit_tags.html',{'data':data}) 


@user_passes_test(superadmin_required, login_url='/login_view') 
def articles(request):
     articles = Article.objects.all().order_by('-created_at')
     return render(request,'dash/articles/article.html',{'articles':articles})

from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse

def search_articles(request):
    term = request.GET.get('term', '')
    articles = Article.objects.filter(title__icontains=term).values('id', 'title')[:20]  # top 20 matches
    data = [{"label": a["title"], "value": a["id"]} for a in articles]
    return JsonResponse(data, safe=False)

@user_passes_test(superadmin_required, login_url='/login_view') 
def add_article(request):
    authors = Author.objects.all()
    categories = Category.objects.all()
    tags = Tags.objects.all()

    if request.method == 'POST':
        # Create Article
        title = request.POST.get('title')
        author_id = request.POST.get('author')
        category_id = request.POST.get('category')
        selected_tag_ids = request.POST.getlist('tags')
        description = request.POST.get('description')
        tldr_title = request.POST.get('tldr_title')
        tldr = request.POST.get('tldr')
        meta_title = request.POST.get('meta_title')
        meta_description = request.POST.get('meta_description')
        meta_keywords = request.POST.get('meta_keywords')
        content = request.POST.get('content')
        status = request.POST.get('status', 'Enabled')
        
        author = Author.objects.get(id=author_id)
        category = Category.objects.get(id=category_id)

        article = Article.objects.create(
            title=title,
            author=author,
            category=category,
            description=description,
            tldr_title=tldr_title,
            tldr=tldr,
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            content=content,
            status=status,
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

    return render(request, 'dash/articles/add_article.html', {
        'authors': authors,
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
    authors = Author.objects.all()
    categories = Category.objects.all()
    tags = Tags.objects.all()
    data = get_object_or_404(Article, id=id)

    if request.method == 'POST':
        # Update article main fields...
        data.title = request.POST.get('title')
        data.description = request.POST.get('description')
        data.tldr_title = request.POST.get('tldr_title')
        data.tldr = request.POST.get('tldr')
        data.meta_title = request.POST.get('meta_title')
        data.meta_description = request.POST.get('meta_description')
        data.meta_keywords = request.POST.get('meta_keywords')
        data.content = request.POST.get('content')
        data.status = request.POST.get('status', 'Enabled')

        data.author = Author.objects.get(id=request.POST.get('author'))
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

    return render(request, 'dash/articles/edit_article.html', {
        'authors': authors,
        'categories': categories,
        'tags': tags,
        'data': data
    })

def disable_article(request,id):
     data = get_object_or_404(Article,id=id)
     data.status = "Disabled"
     data.save()
     return redirect('/articles')

def enable_article(request,id):
     data = get_object_or_404(Article,id=id)
     data.status = "Enabled"
     data.save()
     return redirect('/articles')

def delete_article(request,id):
     data = get_object_or_404(Article,id=id)
     data.delete()
     return redirect('/articles')

def custom_error_handler(request, status_code, exception=None):
    return render(request, 'dash/error.html', {'status_code': status_code, 'message': exception}, status=status_code)

def custom_404(request, exception):
    return custom_error_handler(request, 404, exception)

def custom_500(request):
    return custom_error_handler(request, 500)

def custom_403(request, exception):
    return custom_error_handler(request, 403, exception)

def custom_400(request, exception):
    return custom_error_handler(request, 400, exception)


@user_passes_test(superadmin_required, login_url='/login_view') 
def ad_manager(request):
     adv = Ad.objects.all()
     return render(request,'dash/ad_manager/ads.html',{'adv':adv})

def add_ad(request):
     if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        url = request.POST.get('url')
        Ads =  Ad.objects.create(
            title=title,
            image =  image,
            url = url,
        )
        return redirect('/ad_manager')
     return render(request,'dash/ad_manager/add_ad.html')

def edit_ad(request,id):
     data = get_object_or_404(Ad,id=id)
     if request.method == 'POST':
        data.title = request.POST.get('title')
        data.image = request.FILES.get('image')
        data.url = request.POST.get('url')
        data.save()
        return redirect('/ad_manager')
     return render(request,'dash/ad_manager/edit_ad.html',{'data':data})

def delete_ad(request,id):
     data = get_object_or_404(Ad,id=id)
     data.delete()
     return redirect('/ad_manager')


@user_passes_test(superadmin_required, login_url='/login_view') 
def bstv(request):
     contents = BSTV.objects.all()
     return render(request,'dash/bstv/bstv.html',{'contents':contents})

@user_passes_test(superadmin_required, login_url='/login_view') 
def add_bstv(request):
     categories = Category.objects.all()
     if request.method == 'POST':
        title = request.POST.get('title')
        link = request.POST.get('link')
        description = request.POST.get('description')
        type = request.POST.get('type')
        category = request.POST.get('category')
        status = "Enabled"
        bstv = BSTV.objects.create(
                title=title,
                link=link,
                description=description,
                type=type,
                category=get_object_or_404(Category,id=category),
                status=status,
                thumbnail_image= request.FILES.get('thumbnail_image'),
            )
        return redirect('/bstv')

     return render(request,'dash/bstv/add_bstv.html',{'categories':categories})


def disable_bstv(request,id):
     data = get_object_or_404(BSTV,id=id)
     data.status = "Disabled"
     data.save()
     return redirect('/bstv')

def enable_bstv(request,id):
     data = get_object_or_404(BSTV,id=id)
     data.status = "Enabled"
     data.save()
     return redirect('/bstv')

def delete_bstv(request,id):
     data = get_object_or_404(BSTV,id=id)
     data.delete()
     return redirect('/bstv')

@user_passes_test(superadmin_required, login_url='/login_view') 
def edit_bstv(request,id):
    categories = Category.objects.all()
    data = get_object_or_404(BSTV,id=id)
    if request.method == 'POST':
        data.title = request.POST.get('title')
        data.link = request.POST.get('link')
        data.description = request.POST.get('description')
        data.type = request.POST.get('type')
        # ✅ Correct category assignment
        category_id = request.POST.get('category')
        if category_id:
            data.category = category_id

        # ✅ Correct image assignment
        file = request.FILES.get('thumbnail_image')
        if file:
            data.thumbnail_image = file

        data.save()
        return redirect('/bstv')
    return render(request,'dash/bstv/edit_bstv.html',{'data':data,'categories':categories})


@user_passes_test(superadmin_required, login_url='/login_view') 
def content_management(request):
    all_articles = Article.objects.order_by('-created_at')
    valid_categories = ["BIGSHOT", "UnTHiNK"]
    exclusive_articles = Article.objects.filter().order_by('-created_at')

    # ✅ YouTube videos only
    youtube_videos = BSTV.objects.filter(type="Youtube").order_by('-id')
    reel_videos = BSTV.objects.filter(type="Reel", status="Enabled").order_by('-id')

    # ✅ Get or create selection objects
    challenger_section, _ = TheChallengers.objects.get_or_create(id=1)
    bigshot_section, _ = Bigshot.objects.get_or_create(id=1)
    unthink_section, _ = Unthink.objects.get_or_create(id=1)

    # ✅ Get or create selections
    trending, _ = TrendingArticles.objects.get_or_create(id=1)
    editors_choice, _ = EditorsChoice.objects.get_or_create(id=1)
    trending_buzz, _ = TrendingBuzz.objects.get_or_create(id=1)
    exclusives, _ = Exclusives.objects.get_or_create(id=1)
    exclusives2, _ = Exclusives2.objects.get_or_create(id=1)
    latest_articles, _ = LatestArticles.objects.get_or_create(id=1)
    reel_highlights, _ = ReelsHighlights.objects.get_or_create(id=1)
    

    context = {
        'articles': all_articles,
        'youtube_videos': youtube_videos,
        'exclusive_articles': exclusive_articles,
        'reel_videos':reel_videos,
        'latest_articles':latest_articles,
        'reel_highlights':reel_highlights,
        'trending': trending,
        'editors_choice': editors_choice,
        'trending_buzz': trending_buzz,
        'exclusives': exclusives,
        'exclusives2':exclusives2,
        'challenger_section': challenger_section,
        'bigshot_section': bigshot_section,
        'unthink_section': unthink_section,
    }

    return render(request,'dash/content_manager.html',context)

@user_passes_test(superadmin_required, login_url='/login_view') 
def trending_articles(request):
    trending, created = TrendingArticles.objects.get_or_create(id=1)

    if request.method == "POST":
        selected_ids = request.POST.getlist('in_trend_articles')
        trending.articles.set(selected_ids)  # ✅ cleaner & faster
        trending.save()

    return redirect('/content_management')

@user_passes_test(superadmin_required, login_url='/login_view')
def update_editors_choice(request):
    editors_choice, _ = EditorsChoice.objects.get_or_create(id=1)

    if request.method == "POST":
        selected = request.POST.getlist("editors_choice")
        editors_choice.articles.set(selected)

    return redirect('/content_management')

@user_passes_test(superadmin_required, login_url='/login_view')
def update_trending_buzz(request):
    trending_buzz, _ = TrendingBuzz.objects.get_or_create(id=1)

    if request.method == "POST":
        selected = request.POST.getlist("trending_buzz")
        trending_buzz.videos.set(selected)

    return redirect('/content_management')

@user_passes_test(superadmin_required, login_url='/login_view')
def update_exclusives(request):
    exclusives, _ = Exclusives.objects.get_or_create(id=1)

    if request.method == "POST":
        exclusives.main_article_id = request.POST.get("exclusive_main") or None
        exclusives.articles.set(request.POST.getlist("exclusive_articles"))
        exclusives.save()

    return redirect('/content_management')

@user_passes_test(superadmin_required, login_url='/login_view')
def update_exclusives2(request):
    exclusives2, _ = Exclusives2.objects.get_or_create(id=1)

    if request.method == "POST":

        # ✅ Handle 3 article groups
        exclusives2.article1.set(request.POST.getlist('article1'))
        exclusives2.article2.set(request.POST.getlist('article2'))

        # ✅ Handle reels
        exclusives2.reels.set(request.POST.getlist('reels'))

        exclusives2.save()

    return redirect('/content_management')

@user_passes_test(superadmin_required, login_url='/login_view')
def update_latest_articles(request):
    latest_articles, _ = LatestArticles.objects.get_or_create(id=1)

    if request.method == "POST":
        selected = request.POST.getlist("latest_articles")
        latest_articles.article.set(selected)

    return redirect('/content_management')

@user_passes_test(superadmin_required, login_url='/login_view')
def update_reel_highlights(request):
    reel_highlights, _ = ReelsHighlights.objects.get_or_create(id=1)

    if request.method == "POST":
        selected = request.POST.getlist("reel_highlights")
        reel_highlights.reels.set(selected)

    return redirect('/content_management')

@user_passes_test(superadmin_required, login_url='/login_view')
def update_the_challengers(request):
    obj, _ = TheChallengers.objects.get_or_create(id=1)

    if request.method == "POST":
        obj.Challanger_highlight_id = request.POST.get("challenger_highlight") or None
        obj.suggested.set(request.POST.getlist("challenger_suggested"))
        obj.save()

    return redirect('/content_management')

@user_passes_test(superadmin_required, login_url='/login_view')
def update_bigshot(request):
    obj, _ = Bigshot.objects.get_or_create(id=1)

    if request.method == "POST":
        obj.highlight_id = request.POST.get("bigshot_highlight") or None
        obj.suggested.set(request.POST.getlist("bigshot_suggested"))
        obj.save()

    return redirect('/content_management')

@user_passes_test(superadmin_required, login_url='/login_view')
def update_unthink(request):
    obj, _ = Unthink.objects.get_or_create(id=1)

    if request.method == "POST":
        obj.highlight_id = request.POST.get("unthink_highlight") or None
        obj.suggested.set(request.POST.getlist("unthink_suggested"))
        obj.save()

    return redirect('/content_management')


from dash.analytics import fetch_ga4_data, fetch_youtube_data, fetch_instagram_data 

@user_passes_test(superadmin_required, login_url='/login_view')
def analytics_dashboard(request):
    """
    Fetches live data from GA4, YouTube, and Instagram on every load.
    Each fetch is independent — if one fails the others still show.
    """
    ga4       = fetch_ga4_data()
    youtube   = fetch_youtube_data()
    instagram = fetch_instagram_data()
 
    context = {
        'ga4':       ga4,
        'youtube':   youtube,
        'instagram': instagram,
        'fetched_at': __import__('datetime').datetime.now().strftime('%d %b %Y, %I:%M %p'),
    }
    return render(request, 'dash/analytics.html', context)