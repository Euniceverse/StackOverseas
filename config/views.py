from django.shortcuts import render
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
    # return render(request, 'home.html', {'user': request.user})