from django.shortcuts import render

def homepage(request):
    """Homepage view"""
    return render(request, "homepage.html")

def societiespage(request):
    """Societies page view"""
    return render(request, "societies.html")

def eventspage(request):
    """Events page view"""
    return render(request, "events.html")

def newspage(request):
    """News page view"""
    return render(request, "news.html")

def accountpage(request):
    """My Accounts page view"""
    return render(request, "accounts.html")