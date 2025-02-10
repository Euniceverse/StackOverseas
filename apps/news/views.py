from django.shortcuts import render
from .models import News

def newspage(request):
    """News page view"""
    return render(request, "news.html")

def news_list(request):
    """Retrieve latest 10 published news for news-panel.html"""
    news_queryset = News.objects.filter(is_published=True).order_by("-date_posted")
    return render(request, "news-panel.html", {"news_list": news_queryset})