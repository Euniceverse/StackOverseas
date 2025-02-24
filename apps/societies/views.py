from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Society, SocietyRegistration, Widget
from .functions import approved_societies, get_societies
from .forms import NewSocietyForm
from apps.news.models import News

from config.constants import SOCIETY_TYPE_CHOICES

import json

def societiespage(request):
    # template = get_template('societies.html')
    societies = approved_societies()  # fetch all societies
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {'societies': societies, "news_list": news_list})

def my_societies(request):
    societies = get_societies(request.user)
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {'societies': societies, "news_list": news_list})

@login_required
def create_society(request):
    """Allow a logged-in user to apply for a new society. Max 3."""

    managed_count = Society.objects.filter(manager=request.user).count()

    if managed_count >= 3:
        messages.error(request, "You have reached the maximum of 3 societies.")
        return redirect('societiespage')

    if request.method == "POST":
        form = NewSocietyForm(request.POST)

        if form.is_valid():
            society_registration = form.save(commit=False)
            society_registration.applicant = request.user
            society_registration.status = 'pending'
            society_registration.save()            

            messages.success(request, "Society application submitted. Awaiting approval.")
        
            return redirect('societiespage')
    else:
        form = NewSocietyForm()

    return render(request, 'create_society.html', {'form': form})

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
def top_societies():
    """View to show top 5 societies per type and overall"""

    # get all the society type
    # society_types = Society.objects.values_list('society_type', flat=True).distinct()
    
    # a dictionary to start top societies
    top_societies_per_type = {}
    # print("All Societies:", list(Society.objects.all()))

    all_approved_societies = approved_societies()

    for society_type, _ in SOCIETY_TYPE_CHOICES:
        top_societies_per_type[society_type] = (
            all_approved_societies.filter(society_type=society_type)
            .order_by('-members_count')[:5]
        )


    # for society in SOCIETY_TYPE_CHOICES[0]:
    #     top_societies_per_type[society] = (
    #         Society.objects.filter(society_type=society)
    #         .order_by('-members_count')[:5]  
    #     )

    top_overall_societies = Society.objects.order_by('-members_count')[:5]
    '''
    print("Top Overall Societies:", list(top_overall_societies))
    print("Top Societies Per Type:", top_societies_per_type)
    '''
    return({'top_overall_societies':top_overall_societies,'top_societies_per_type':top_societies_per_type})
    # return render(request, "home.html", {
    #     "top_societies_per_type": top_societies_per_type,
    #     "top_overall_societies": top_overall_societies,
    #     'user' : request.user
    # })
    
@login_required
def society_admin_view(request, society_id):
    """View for society managers to configure the society page"""
    society = get_object_or_404(Society, id=society_id)

    if request.user != society.manager:
        messages.error(request, "You are not authorized to edit this society.")
        return redirect("society_page", society_id=society.id)

    if request.method == "POST":
        widget_type = request.POST.get("widget_type")
        Widget.objects.create(society=society, widget_type=widget_type, position=Widget.objects.filter(society=society).count())
        messages.success(request, f"{widget_type} widget added!")

    widgets = Widget.objects.filter(society=society).order_by("position")

    return render(request, "society_admin.html", {"society": society, "widgets": widgets})

@login_required
def remove_widget(request, society_id, widget_id):
    """Allows society managers to remove widgets"""
    widget = get_object_or_404(Widget, id=widget_id, society_id=society_id)

    if request.user != widget.society.manager:
        messages.error(request, "You are not authorized to delete this widget.")
        return redirect("society_admin_view", society_id=society_id)

    widget.delete()
    messages.success(request, "Widget removed successfully.")
    return redirect("society_admin_view", society_id=society_id)

def society_page(request, society_id):
    """Public society page that displays widgets dynamically."""
    society = get_object_or_404(Society, id=society_id)
    widgets = Widget.objects.filter(society=society).order_by("position")

    # determine user access level
    is_member = society.members.filter(id=request.user.id).exists() if request.user.is_authenticated else False
    is_manager = request.user == society.manager if request.user.is_authenticated else False
    
    # remove member-only widgets for non-members
    if not is_member:
        widgets = widgets.exclude(widget_type__in=["discussion", "members"])

    return render(
        request,
        "society_page.html",
        {
            "society": society,
            "widgets": widgets,
            "is_member": is_member,
            "is_manager": is_manager,
        },
    )
    
