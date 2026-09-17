from dash.models import Article  # or whatever your model is called

def global_context(request):
    # Latest 3 articles
    excluded_ids = [7, 23, 24, 25]
    latest_articles = Article.objects.exclude(category__id__in=excluded_ids,status="Enabled").order_by('-created_at')[:6]
    bigshot_articles_header =  Article.objects.filter(category__id__in=[25],status="Enabled").order_by('-created_at')[:5]
    unthink_articles_header =  Article.objects.filter(category__id__in=[23],status="Enabled").order_by('-created_at')[:5]
    thechallengers_articles_header =  Article.objects.filter(category__id__in=[7],status="Enabled").order_by('-created_at')[:5]
    gov360_articles_header =  Article.objects.filter(category__id__in=[28],status="Enabled").order_by('-created_at')[:5]
    expertdiaries_articles_header =  Article.objects.filter(category__id__in=[19],status="Enabled").order_by('-created_at')[:5]
    bharat_one_articles = Article.objects.filter(category__id__in=[17],status="Enabled").order_by('-created_at')[:5]
    return {
        'latest_articles': latest_articles,
        'bigshot_articles_header':bigshot_articles_header,
        'unthink_articles_header':unthink_articles_header,
        'thechallengers_articles_header':thechallengers_articles_header,
        'gov360_articles_header':gov360_articles_header,
        'expertdiaries_articles_header':expertdiaries_articles_header,
        'bharat_one_articles':bharat_one_articles,
    }
