from .models import Society, Membership, MembershipRole, MembershipStatus
from .functions import approved_societies, get_societies, manage_societies, get_all_users
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import NewSocietyForm, JoinSocietyForm
from apps.news.models import News
from django.db.models import Count
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Society, SocietyRegistration, Widget
from .forms import NewSocietyForm
from apps.news.models import News
from config.filters import SocietyFilter
from config.constants import SOCIETY_TYPE_CHOICES
import json

def societiespage(request):
    societies = Society.objects.all()

    # Apply filters
    filtered_societies = SocietyFilter(request.GET, queryset=societies).qs

    # Sorting
    sort_option = request.GET.get("sort", "name_asc")

    if sort_option == "name_asc":
        filtered_societies = filtered_societies.order_by("name")
    elif sort_option == "name_desc":
        filtered_societies = filtered_societies.order_by("-name")
    elif sort_option == "date_created":
        filtered_societies = filtered_societies.order_by("created_at")
    elif sort_option == "price_low_high":
        filtered_societies = filtered_societies.order_by("price_range")
    elif sort_option == "price_high_low":
        filtered_societies = filtered_societies.order_by("-price_range")
    elif sort_option == "popularity":
        filtered_societies = filtered_societies.order_by("-members_count")

    return render(request, "societies.html", {"societies": filtered_societies})


def my_societies(request):
    societies = get_societies(request.user)
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {'societies': societies, "news_list": news_list, 'page':'My'})

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

            return redirect('manage_societies')

        elif 'cancel' in request.POST:
            return redirect('manage_societies')

    return render(request, 'admin_confirm_decision.html', {
        'society': society,
        'action': action
    })

def view_manage_societies(request):
    to_manage = manage_societies()
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {'societies': to_manage, "news_list": news_list, 'page':'Manange'})


# def top_societies():
    """View to show top 5 societies per type and overall"""


@login_required
def manage_society(request, society_id):
    """
    Display a page listing all current Membership objects for this society.
    Only the manager or co_manager may view this page.
    """
    society = get_object_or_404(Society, id=society_id)

    # Check if request.user is the manager (the one who created the society):
    if society.manager == request.user:
        is_authorized = True
    else:
        # Or check if they are a co_manager of this society
        co_manager_membership = Membership.objects.filter(
            society=society,
            user=request.user,
            role=MembershipRole.CO_MANAGER,
            status=MembershipStatus.APPROVED
        ).first()
        is_authorized = bool(co_manager_membership)

    if not is_authorized:
        messages.error(request, "You do not have permission to manage this society.")
        return redirect('societiespage')

    # Get all memberships for this society
    memberships = Membership.objects.filter(society=society).select_related('user')

    return render(request, 'manage_society.html', {
        'society': society,
        'memberships': memberships,
        'user' : request.user
    })

def view_all_members(request):
    if request.user.is_superuser:
        # all_members = get_all_users()
        society = get_object_or_404(Society, id=1)
        all_members = Membership.objects.select_related("user", "society").all()
        return render(request, 'manage_society.html', {
        'society': society,
        'memberships': all_members,
        'user' : request.user
    })
    else:
        messages.error(request, "You do not have permission to view all members.")
        return redirect('societiespage')

@login_required
def update_membership(request, society_id, user_id):

    society = get_object_or_404(Society, id=society_id)
    membership = get_object_or_404(Membership, society=society, user_id=user_id)

    # Double-check the request.user is allowed to manage
    # i.e. they are the society manager or co-manager
    if society.manager == request.user:
        pass
    else:
        co_manager_membership = Membership.objects.filter(
            society=society,
            user=request.user,
            role=MembershipRole.CO_MANAGER,
            status=MembershipStatus.APPROVED
        ).first()
        if not co_manager_membership:
            messages.error(request, "You do not have permission to update members for this society.")
            return redirect('societiespage')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            membership.status = MembershipStatus.APPROVED
            membership.save()
            messages.success(request, f"{membership.user.email} has been approved!")
        
        elif action == 'remove':
            # Remove the membership entirely
            membership.delete()
            messages.success(request, f"{membership.user.email} has been removed from {society.name}.")
        
        elif action == 'promote_co_manager':
            membership.role = MembershipRole.CO_MANAGER
            membership.status = MembershipStatus.APPROVED  # ensure they are now approved
            membership.save()
            messages.success(request, f"{membership.user.email} is now a Co-Manager.")
        
        elif action == 'promote_editor':
            membership.role = MembershipRole.EDITOR
            membership.status = MembershipStatus.APPROVED
            membership.save()
            messages.success(request, f"{membership.user.email} is now an Editor.")
        
        return redirect('manage_society', society_id=society_id)
    
    # If it's not POST, just redirect back
    return redirect('manage_society', society_id=society_id)

def society_detail(request, society_id):
    """Temporary society detail page just to show a Manage This Society button."""
    society = get_object_or_404(Society, id=society_id)
    memberships = Membership.objects.filter(society=society)
    
    user_membership = memberships.filter(user=request.user).first() if request.user.is_authenticated else None

    return render(request, 'society_page.html', {
        'society': society,
        'memberships': memberships,
        'user_membership': user_membership, 
    })
    #return render(request, 'society_page.html', {'society': society})

@login_required
def join_society(request, society_id):
    """Display the join form for a society and handle submission."""
    society = get_object_or_404(Society, id=society_id)

    # Check if user is already in the membership table with an approved or pending status
    existing_member = Membership.objects.filter(society=society, user=request.user).first()
    if existing_member and existing_member.status in [MembershipStatus.APPROVED, MembershipStatus.PENDING]:
        messages.info(request, "You are already a member or have an application pending.")
        return redirect('society_page', society_id=society.id)

    if request.method == 'POST':
        form = JoinSocietyForm(society=society, user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            application = form.create_membership_and_application()
            if application.is_approved:
                messages.success(request, "You have joined the society successfully!")
            elif application.is_rejected:
                messages.error(request, "Your application was rejected based on your answers.")
            else:
                messages.info(request, "Your application has been submitted and is pending approval.")
            return redirect('society_page', society_id=society.id)
    else:
        form = JoinSocietyForm(society=society, user=request.user)

    return render(request, 'join_society.html', {
        'society': society,
        'form': form
    })


@login_required
def view_applications(request, society_id):
    from .models import MembershipApplication
    """If the society is set to 'manual' or has any applications, managers can see them here."""
    society = get_object_or_404(Society, id=society_id)
    # Only manager or co_manager can see
    is_manager_or_co = False
    if society.manager == request.user:
        is_manager_or_co = True
    else:
        from .models import MembershipRole
        membership_co = Membership.objects.filter(
            society=society,
            user=request.user,
            role=MembershipRole.CO_MANAGER,
            status=MembershipStatus.APPROVED
        ).first()
        is_manager_or_co = bool(membership_co)

    if not is_manager_or_co:
        messages.error(request, "You do not have permission to view applications.")
        return redirect('society_page', society_id=society.id)

    # Show all membership applications for this society
    applications = society.applications.filter(is_approved=False, is_rejected=False)

    return render(request, "view_applications.html", {
        'society': society,
        'applications': applications,
    })


@login_required
def decide_application(request, society_id, application_id, decision):
    from .models import MembershipApplication
    """Manager or co-manager can approve or reject an application with requirement_type=manual."""
    society = get_object_or_404(Society, id=society_id)
    application = get_object_or_404(society.applications, id=application_id)
    # same manager check
    is_manager_or_co = False
    if society.manager == request.user:
        is_manager_or_co = True
    else:
        from .models import MembershipRole
        membership_co = Membership.objects.filter(
            society=society,
            user=request.user,
            role=MembershipRole.CO_MANAGER,
            status=MembershipStatus.APPROVED
        ).first()
        is_manager_or_co = bool(membership_co)

    if not is_manager_or_co:
        messages.error(request, "You do not have permission to decide on applications.")
        return redirect('society_page', society_id=society.id)

    if decision not in ['approve', 'reject']:
        messages.error(request, "Invalid decision.")
        return redirect('view_applications', society_id=society.id)

    if decision == 'approve':
        application.is_approved = True
        application.save()
        # Update membership
        membership, created = Membership.objects.get_or_create(
            society=society,
            user=application.user,
            defaults={'role': 'member', 'status': 'pending'}
        )
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
        membership.status = MembershipStatus.APPROVED
        membership.save()
        messages.success(request, f"Application for {application.user.email} approved.")
    else:
        application.is_rejected = True
        application.save()
        # remove membership if any
        Membership.objects.filter(society=society, user=application.user).delete()
        messages.warning(request, f"Application for {application.user.email} rejected.")


    return redirect('view_applications', society_id=society.id)


    # top_overall_societies = all_approved_socities.order_by('-members_count')[:5]
    # '''
    # print("Top Overall Societies:", list(top_overall_societies))
    # print("Top Societies Per Type:", top_societies_per_type)
    # '''
    # return({'top_overall_societies':top_overall_societies,'top_societies_per_type':top_societies_per_type})
    # # return render(request, "home.html", {
    # #     "top_societies_per_type": top_societies_per_type,
    # #     "top_overall_societies": top_overall_societies,
    # #     'user' : request.user
    # # })

# handle when manager wants to delete the society
def request_delete_society(request, society_id):
    society = get_object_or_404(Society, id=society_id)
    #society = Society.objects.filter(id=society_id, manager=request.user).first()

    if request.method == "POST":
        if society.members_count >= 100:
            society.status = 'request_delete'
            society.visibility = 'Private' 
            messages.info(request, "Your deletion request is pending admin approval.")
        else:
            society.status = 'deleted'
            messages.success(request, "Your society was automatically deleted.")

        society.updated_at = now()
        society.save()
        return redirect('societiespage')

    return render(request, "request_delete_society.html", {"society": society})

# when need the admin approval
@user_passes_test(lambda user: user.is_staff)
def admin_confirm_delete(request, society_id):
    society = get_object_or_404(Society, id=society_id, status='request_delete')
  
    if request.method == "POST":
        action = request.POST.get("action")
        print("Action received:", action) 
        if action == "approve":
            society.status = "deleted"
            print(f"Updating {society.name} status to 'deleted'") 
            messages.success(request, f"Society '{society.name}' has been deleted.")
        elif action == "reject":
            society.status = "approved"
            print(f"Updating {society.name} status to 'approved'")  
            messages.warning(request, f"Society '{society.name}' deletion request was rejected.")

        society.save()
        return redirect('societiespage')

    return render(request, "admin_confirm_delete.html", {
        "society": society,
        "action": None
    })
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
    
@csrf_exempt
#@login_required
def update_widget_order(request, society_id):
    """Update widget order when the manager rearranges widgets."""
    if request.method == "POST":
        society = get_object_or_404(Society, id=society_id)
        
        # ensures only the manager can update order
        if request.user != society.manager:
            return JsonResponse({"error": "Permission denied"}, status=403)

        try:
            data = json.loads(request.body)
            widget_order = data.get("widget_order", [])
            
            for index, widget_id in enumerate(widget_order):
                widget = Widget.objects.get(id=widget_id, society=society)
                widget.position = index
                widget.save()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)
