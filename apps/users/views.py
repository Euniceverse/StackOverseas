from django.shortcuts import render

def accountpage(request):
    """My Accounts page view"""
    return render(request, "accounts.html")
