from django.shortcuts import render
from .models import News

def newspage(request):
    """News page view"""
    return render(request, "news.html")

def news_list(request):
    news = News.objects.filter(is_published=True).order_by("-date_posted")
    return render(request, "news.html", {"news_list": news_list})