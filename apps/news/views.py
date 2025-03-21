from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F
from apps.societies.models import Society
from .models import News
from .forms import NewsForm
from config.filters import NewsFilter
from config.constants import SOCIETY_TYPE_CHOICES
from apps.societies.models import Membership, MembershipStatus

def newspage(request):
    """News page with filtering and sorting"""
    news = News.objects.all()

    # apply filtering
    filtered_news = NewsFilter(request.GET, queryset=news).qs

    # sorting option depend on request
    sort_option = request.GET.get("sort", "newest")

    if sort_option == "newest":
        filtered_news = filtered_news.order_by("-date_posted")
    elif sort_option == "oldest":
        filtered_news = filtered_news.order_by("date_posted")
    elif sort_option == "popularity":
        filtered_news = filtered_news.order_by("-views")  # assume: `views` field tracks popularity

    societies = Society.objects.filter(status="approved")

    return render(request, "news.html", {
        "news_list": filtered_news,
        "societies": societies,
        "SOCIETY_TYPE_CHOICES": SOCIETY_TYPE_CHOICES,
        "selected_sort": sort_option,
    })

def news_list(request):
    """Retrieve latest 10 published news for news-panel.html"""
    news_queryset = News.objects.filter(is_published=True).order_by("-date_posted")
    return render(request, "news-panel.html", {"news_list": news_queryset})

@login_required
def create_news(request):
    """Create a news post."""
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

@login_required
def edit_news(request, news_id):
    news_item = get_object_or_404(News, id=news_id)

    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES, instance=news_item, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("news_list")
    else:
        form = NewsForm(instance=news_item, user=request.user)
    
    return render(request, "edit_news.html", {"form": form, "news_item": news_item})

def news_detail(request, news_id):
    """Display a single news article and increment view count"""
    news = get_object_or_404(News, id=news_id)
    news.views = F("views") + 1  # increase views
    news.save(update_fields=["views"])  # save without changing time

    user_membership = None
    if request.user.is_authenticated:
        user_membership = Membership.objects.filter(
            society=news.society,
            user=request.user,
            status=MembershipStatus.APPROVED
        ).first()

    context = {
        "news": news,
        "user_membership": user_membership,
    }
    return render(request, "news_detail.html", context)

@login_required
def delete_news(request, news_id):
    news_item = get_object_or_404(News, id=news_id)
    # Example permission check: only allow if the user is a manager, co_manager, editor for the society or is superuser.
    if not (request.user.is_superuser or (hasattr(request, 'user_membership') and request.user_membership.role in ['manager', 'co_manager', 'editor'])):
        messages.error(request, "You do not have permission to delete this news.")
        return redirect('news_detail', news_id=news_id)
    news_item.delete()
    messages.success(request, "News deleted successfully!")
    return redirect('news_list')
