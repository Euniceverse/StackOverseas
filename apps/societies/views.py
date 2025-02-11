from django.shortcuts import render
from .models import Society
from django.db.models import Count



def societiespage(request):
    """Societies page view"""
    return render(request, "societies.html")

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


    return render(request, "homepage.html", {
        "top_societies_per_type": top_societies_per_type,
        "top_overall_societies": top_overall_societies,
    })