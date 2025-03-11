from django.shortcuts import render
from .functions import search_societies
from apps.societies.functions import top_societies

def home(request):
    """Display the main page.
    Shows login/signup buttons for anonymous users,
    and user-specific content for authenticated users."""
    disct_soc = top_societies(request.user)
    return render(request, "home.html", {
        "top_societies_per_type": disct_soc['top_societies_per_type'],
        "top_overall_societies": disct_soc['top_overall_societies'],
        'user' : request.user
    })

def ai_search(request):
    """Handle the AI-powered search request."""
    query = request.GET.get('q', '')
    search_type = request.GET.get('search_type', 'societies')

    if search_type == 'events':
        # Handle event search
        from apps.events.models import Event
        events = Event.objects.filter(name__icontains=query)
        return render(request, 'events.html', {
            'events': events,
            'page': 'Search Results'
        })
    else:
        # Handle society search (default)
        results, suggestion = search_societies(query)
        return render(request, 'societies.html', {
            'societies': results,
            'page': 'Search',
            'suggestion': suggestion
        })
