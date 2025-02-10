from django.shortcuts import render
from apps.news.models import News

def societiespage(request):
    """Societies page view"""
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {"news_list": news_list})
