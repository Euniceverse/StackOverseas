from django.shortcuts import render

def eventspage(request):
    """Events page view"""
    return render(request, "events.html")