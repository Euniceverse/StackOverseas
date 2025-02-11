from django.shortcuts import render

from .models import Society
from apps.news.models import News
# from django.template.loader import get_template

def societiespage(request):
    # template = get_template('societies.html')
    societies = Society.objects.all()  # Fetch all societies
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {'societies': societies, "news_list": news_list})


