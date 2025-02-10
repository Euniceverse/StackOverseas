from django.shortcuts import render
from apps.news.models import News

def eventspage(request):
    """Events page view"""
    return render(request, "events.html")

    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "events.html", {"news_list": news_list})
