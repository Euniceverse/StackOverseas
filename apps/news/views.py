from django.shortcuts import render

def newspage(request):
    """News page view"""
    return render(request, "news.html")
