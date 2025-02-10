from django.shortcuts import render
from .models import News

def newspage(request):
    """News page view"""
    return render(request, "news.html")

def news_list(request):
    news = News.objects.filter(is_published=True).order_by("-date_created")
    return render(request, "news_list.html", {"news": news})