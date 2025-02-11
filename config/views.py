from django.shortcuts import render
from apps.news.models import News

def homepage(request):
    """Homepage view"""
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]  
    return render(request, "homepage.html", {"news_list": news_list})
