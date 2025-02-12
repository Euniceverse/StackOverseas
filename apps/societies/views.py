from django.shortcuts import render, redirect

from .models import Society
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import NewSocietyForm
from apps.news.models import News
from django.db.models import Count



def societiespage(request):
    # template = get_template('societies.html')
    societies = Society.objects.all()  # Fetch all societies
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {'societies': societies, "news_list": news_list})

@login_required
def create_society(request):
    """Allow a logged-in user to create a new society, limited to 3 societies max."""

    managed_count = Society.objects.filter(manager=request.user).count()

    if managed_count >= 3:
        messages.error(request, "You have reached the maximum of 3 societies.")
        return redirect('societiespage')

    if request.method == "POST":
        form = NewSocietyForm(request.POST)
        if form.is_valid():
        
            new_society = Society.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                society_type=form.cleaned_data['society_type'],
                manager=request.user, 
                status='pending'  # initially set to pending
            )

            messages.success(request, "Society created. Status pending.")
        
            return redirect('societiespage')
    else:
        form = NewSocietyForm()

    return render(request, 'societies/create_society.html', {'form': form})

def admin_check(user):
    return user.is_staff or user.is_superuser

@user_passes_test(admin_check)
def admin_pending_societies(request):
    """List all societies that are still pending, allowing admin to choose approve/reject."""
    pending_socs = Society.objects.filter(status='pending')
    return render(request, 'societies/admin_pending_societies.html', {
        'pending_socs': pending_socs
    })

@user_passes_test(admin_check)
def admin_confirm_society_decision(request, society_id, action):
    """
    Step 1: Show a confirmation page when admin clicks Approve/Reject.
    Step 2: If the admin POSTs 'Confirm', finalize the action:
      - Approve: set status='approved', visibility='private' (if your model has it)
      - Reject: delete or set status='rejected'
    """
    society = get_object_or_404(Society, id=society_id, status='pending')

    if request.method == 'POST':
        if 'confirm' in request.POST:
            if action == 'approve':
                society.status = 'approved'
                # need to set to private
                society.save()
                messages.success(request, f"Society '{society.name}' has been approved and set to private.")
            elif action == 'reject':
                society.delete()  # or set status='rejected' if you prefer
                messages.warning(request, f"Society '{society.name}' has been rejected and discarded.")

            return redirect('admin_pending_societies')

        elif 'cancel' in request.POST:
            return redirect('admin_pending_societies')

    return render(request, 'societies/admin_confirm_decision.html', {
        'society': society,
        'action': action
    })
def top_societies(request):
    """View to show top 5 societies per type and overall"""

    # get all the society type
    society_types = Society.objects.values_list('society_type', flat=True).distinct()

    # a dictionary to start top societies
    top_societies_per_type = {}

    for society in society_types:
        top_societies_per_type[society] = (
            Society.objects.filter(society_type=society)
            .order_by('-members_count')[:5]  
        )

    top_overall_societies = Society.objects.order_by('-members_count')[:5]

    print("Top Overall Societies:", list(top_overall_societies))
    print("Top Societies Per Type:", top_societies_per_type)


    return render(request, "home.html", {
        "top_societies_per_type": top_societies_per_type,
        "top_overall_societies": top_overall_societies,
    })