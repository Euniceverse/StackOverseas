from django.shortcuts import render

def societiespage(request):
    """Societies page view"""
    return render(request, "societies.html")
