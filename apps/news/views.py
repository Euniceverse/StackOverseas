from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.societies.models import Society
from .models import News
from .forms import NewsForm
from config.filters import NewsFilter
from config.constants import SOCIETY_TYPE_CHOICES

def newspage(request):
    """News page with filtering"""
    news = News.objects.all()
    filtered_news = NewsFilter(request.GET, queryset=news).qs
    societies = Society.objects.filter(status="approved")  # Fetch approved societies

    return render(request, "news.html", {
        "news_list": filtered_news,
        "societies": societies,  # Pass societies to template
        "SOCIETY_TYPE_CHOICES": SOCIETY_TYPE_CHOICES,  # Keep this for society type filter
    })


#def newspage(request):
#    """News page view"""
#    return render(request, "news.html")

def news_list(request):
    """Retrieve latest 10 published news for news-panel.html"""
    news_queryset = News.objects.filter(is_published=True).order_by("-date_posted")
    return render(request, "news-panel.html", {"news_list": news_queryset})

@login_required
def create_news(request):
    """Create a news post."""
    # fetch societies managed by the logged-in user
    managed_societies = Society.objects.filter(manager=request.user)

    if not managed_societies.exists():
        messages.error(request, "You do not manage any societies.")
        return redirect("home")

    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            news = form.save(commit=False)

            try:
                selected_society = Society.objects.get(id=int(request.POST["society"]))
            except (Society.DoesNotExist, ValueError):
                messages.error(request, "Invalid society selection.")
                return redirect("create_news")

            if not managed_societies.filter(id=selected_society.id).exists():
                messages.error(request, "You are not authorized to post news for this society.")
                return redirect("create_news")

            if "save_draft" in request.POST:
                news.is_published = False
                messages.success(request, "News saved as draft!")
            elif "post" in request.POST:
                news.is_published = True
                messages.success(request, "News successfully posted!")

            news.save()
            messages.success(request, "News successfully created!")
            return redirect("news_list")
    else:
        form = NewsForm(user=request.user)

    return render(request, "create_news.html", {"form": form})
