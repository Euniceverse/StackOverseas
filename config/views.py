from django.shortcuts import render

def home(request):
    """Display the main page.
    Shows login/signup buttons for anonymous users,
    and user-specific content for authenticated users."""

    return render(request, 'home.html', {'user': request.user})