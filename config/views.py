from django.shortcuts import render
from .functions import search_societies, get_recent_news
from apps.societies.functions import top_societies

def home(request):
    """Display the main page.
    Shows login/signup buttons for anonymous users,
    and user-specific content for authenticated users."""
    recent_news = get_recent_news()
    disct_soc = top_societies(request.user)
    return render(request, "home.html", {
        "news_list": recent_news,
        "top_societies_per_type": disct_soc['top_societies_per_type'],
        "top_overall_societies": disct_soc['top_overall_societies'],
        "user": request.user,
    })

def ai_search(request):
    """Handle the AI-powered search request."""
    query = request.GET.get('q', '')
    search_type = request.GET.get('search_type', 'societies')

    if search_type == 'events':
        # Handle event search using the AI search function
        from .functions import search_events
        results, suggestion = search_events(query)

        request.session['search_type'] = 'events'
        request.session['search_ids'] = [e.id for e in results]

        recent_news = get_recent_news()
        top_context = top_societies(request.user)

        return render(request, 'events_search.html', {
            'events': results,
            'page': 'Search Results',
            'suggestion': suggestion,
            'search_type': 'events',
            'news_list': recent_news,
            **top_context,
        })
    else:
        # Handle society search (default)
        results, suggestion = search_societies(query)

        request.session['search_type'] = 'societies'  # changed
        request.session['search_ids'] = [s.id for s in results]

        recent_news = get_recent_news()
        top_context = top_societies(request.user)

        return render(request, 'societies.html', {
            'societies': results,
            'page': 'Search',
            'suggestion': suggestion,
            'news_list': recent_news,
            **top_context,
        })
