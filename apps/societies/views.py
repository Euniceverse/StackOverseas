from django.shortcuts import render

from .models import Society
from apps.news.models import News
# from django.template.loader import get_template
from .models import Society
from django.db.models import Count



def societiespage(request):
    # template = get_template('societies.html')
    societies = Society.objects.all()  # Fetch all societies
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {'societies': societies, "news_list": news_list})

def top_societies(request):
    """View to show top 5 societies per type and overall"""

    # get all the society type
    society_types = Society.objects.values_list('society_type', flat=True).distinct()

    # a dictionary to start top societies
    top_societies_per_type = {}

    for society in society_types:
        top_societies_per_type[society] = (
            Society.objects.filter(society_type=society)
            .order_by('-members_count')[:5]  
        )

    top_overall_societies = Society.objects.order_by('-members_count')[:5]

    print("Top Overall Societies:", list(top_overall_societies))
    print("Top Societies Per Type:", top_societies_per_type)


    return render(request, "home.html", {
        "top_societies_per_type": top_societies_per_type,
        "top_overall_societies": top_overall_societies,
    })