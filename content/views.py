from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from dash.models import Author, Category, BSTV


# ─────────────────────────────────────────
#  Auth guard — must have an author profile
# ─────────────────────────────────────────

def author_required(user):
    if not user.is_authenticated:
        return False
    try:
        _ = user.author_profile
        return True
    except Exception:
        return False


# ─────────────────────────────────────────
#  LOGIN / LOGOUT
# ─────────────────────────────────────────

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
    return render(request, 'content/signin.html')


def logout_view(request):
    logout(request)
    return redirect('/login_view')


# ─────────────────────────────────────────
#  BSTV — list (my videos only)
# ─────────────────────────────────────────

@user_passes_test(author_required, login_url='/login_view')
def bstv(request):
    author   = request.user.author_profile
    contents = BSTV.objects.all().order_by('-id')
    return render(request, 'content/bstv/bstv.html', {'contents': contents, 'author': author})


# ─────────────────────────────────────────
#  BSTV — add
# ─────────────────────────────────────────

@user_passes_test(author_required, login_url='/login_view')
def add_bstv(request):
    author     = request.user.author_profile
    categories = Category.objects.filter(status='Enabled')

    if request.method == 'POST':
        BSTV.objects.create(
            title=request.POST.get('title'),
            link=request.POST.get('link'),
            description=request.POST.get('description'),
            type=request.POST.get('type'),
            category=request.POST.get('category'),
            status='Disabled',                          # admin enables after review
            thumbnail_image=request.FILES.get('thumbnail_image'),
        )
        return redirect('/bstv')

    return render(request, 'content/bstv/add_bstv.html', {
        'categories': categories,
        'author':     author,
    })


# ─────────────────────────────────────────
#  BSTV — edit
# ─────────────────────────────────────────

@user_passes_test(author_required, login_url='/login_view')
def edit_bstv(request, id):
    author     = request.user.author_profile
    data       = get_object_or_404(BSTV, id=id)
    categories = Category.objects.filter(status='Enabled')

    if request.method == 'POST':
        data.title       = request.POST.get('title')
        data.link        = request.POST.get('link')
        data.description = request.POST.get('description')
        data.type        = request.POST.get('type')
        data.category    = request.POST.get('category')

        file = request.FILES.get('thumbnail_image')
        if file:
            data.thumbnail_image = file

        data.save()
        return redirect('/bstv')

    return render(request, 'content/bstv/edit_bstv.html', {
        'data':       data,
        'categories': categories,
        'author':     author,
    })


# ─────────────────────────────────────────
#  BSTV — AJAX search (for task attach)
# ─────────────────────────────────────────

def search_bstv(request):
    term = request.GET.get('term', '').strip()

    if not hasattr(request.user, 'author_profile'):
        return JsonResponse([], safe=False)

    items = BSTV.objects.filter(
        title__icontains=term,
        status='Enabled'
    ).values('id', 'title', 'type', 'category')[:20]

    data = [{'label': f"{i['title']} ({i['type']})", 'value': i['id']} for i in items]
    return JsonResponse(data, safe=False)


# ─────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────

@user_passes_test(author_required, login_url='/login_view')
def profile(request):
    profile = request.user.author_profile
    return render(request, 'content/editors/profile.html', {'profile': profile})


@user_passes_test(author_required, login_url='/login_view')
def edit_editor(request):
    data = request.user.author_profile

    if request.method == 'POST':
        data.name          = request.POST.get('name')
        data.designation   = request.POST.get('designation')
        data.description   = request.POST.get('description')
        data.email         = request.POST.get('email')
        data.DOB           = request.POST.get('DOB')
        data.location      = request.POST.get('location')
        data.facebook_url  = request.POST.get('facebook_url')
        data.instagram_url = request.POST.get('instagram_url')
        data.linkedin_url  = request.POST.get('linkedin_url')
        data.twitter_url   = request.POST.get('twitter_url')

        if request.FILES.get('image'):
            data.image = request.FILES.get('image')

        data.save()
        return redirect('/profile')

    return render(request, 'content/editors/edit_editors.html', {'data': data})


# ─────────────────────────────────────────
#  ERROR HANDLERS
# ─────────────────────────────────────────

def custom_error_handler(request, status_code, exception=None):
    return render(request, 'content/error.html', {
        'status_code': status_code,
        'message':     exception,
    }, status=status_code)

def custom_404(request, exception):
    return custom_error_handler(request, 404, exception)

def custom_500(request):
    return custom_error_handler(request, 500)

def custom_403(request, exception):
    return custom_error_handler(request, 403, exception)

def custom_400(request, exception):
    return custom_error_handler(request, 400, exception)