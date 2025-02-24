from django.shortcuts import render, redirect


from .models import Society, Membership, MembershipRole, MembershipStatus
from .functions import approved_socities, get_societies, manage_societies

from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import NewSocietyForm, JoinSocietyForm
from apps.news.models import News
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404

from config.constants import SOCIETY_TYPE_CHOICES


def societiespage(request):
    # template = get_template('societies.html')
    societies = approved_socities()  # fetch all societies
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {'societies': societies, "news_list": news_list, 'page':'All'})

def my_societies(request):
    societies = get_societies(request.user)
    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {'societies': societies, "news_list": news_list, 'page':'My'})

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
                status='pending',  # initially set to pending
                visibility='Private'
            )

            messages.success(request, "Society created. Status pending.")
        
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

    return render(request, 'societies/manage_society.html', {
        'society': society,
        'memberships': memberships,
    })


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
    return render(request, 'societies/society_detail.html', {'society': society})

@login_required
def join_society(request, society_id):
    """Display the join form for a society and handle submission."""
    society = get_object_or_404(Society, id=society_id)

    # Check if user is already in the membership table with an approved or pending status
    existing_member = Membership.objects.filter(society=society, user=request.user).first()
    if existing_member and existing_member.status in [MembershipStatus.APPROVED, MembershipStatus.PENDING]:
        messages.info(request, "You are already a member or have an application pending.")
        return redirect('society_detail', society_id=society.id)

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
            return redirect('society_detail', society_id=society.id)
    else:
        form = JoinSocietyForm(society=society, user=request.user)

    return render(request, 'societies/join_society.html', {
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
        return redirect('society_detail', society_id=society.id)

    # Show all membership applications for this society
    applications = society.applications.filter(is_approved=False, is_rejected=False)

    return render(request, "societies/view_applications.html", {
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
        return redirect('society_detail', society_id=society.id)

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

