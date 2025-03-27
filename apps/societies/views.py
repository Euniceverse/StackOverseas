from .models import Society, Membership, MembershipRole, MembershipStatus, RequirementType
from .functions import approved_societies, get_societies, manage_societies, get_all_users, top_societies
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import NewSocietyForm, JoinSocietyForm
from apps.news.models import News
from django.db.models import Count
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.timezone import now, timezone

from .models import Society, SocietyRegistration
from .forms import NewSocietyForm
from apps.news.models import News
from config.functions import get_recent_news
from apps.widgets.models import Widget
from config.filters import SocietyFilter
from config.constants import SOCIETY_TYPE_CHOICES
import json

def societiespage(request):
    societies = approved_societies(request.user)

    # Apply filters
    filtered_societies = SocietyFilter(request.GET, queryset=societies).qs

    # Sorting
    sort_option = request.GET.get("sort", "name_asc")

    # news panel news
    recent_news = get_recent_news()

    if sort_option == "name_asc":
        filtered_societies = filtered_societies.order_by("name")
    elif sort_option == "name_desc":
        filtered_societies = filtered_societies.order_by("-name")
    elif sort_option == "date_newest":
        filtered_societies = filtered_societies.order_by("-created_at")
    elif sort_option == "date_oldest":
        filtered_societies = filtered_societies.order_by("created_at")
    elif sort_option == "price_low_high":
        filtered_societies = filtered_societies.order_by("joining_fee")
    elif sort_option == "price_high_low":
        filtered_societies = filtered_societies.order_by("-joining_fee")
    elif sort_option == "popularity":
        filtered_societies = filtered_societies.order_by("-members_count")
    elif sort_option == "availability":
        filtered_societies = filtered_societies.order_by("members_count")


    top_context = top_societies(request.user)
    recent_news = get_recent_news()

    context = {
        "societies": filtered_societies,
        "news_list": recent_news,
        **top_context
    }

    return render(request, "societies.html", context)


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

            # Create a Society instance for admin visibility
            new_society = Society.objects.create(
                name=society_registration.name,
                description=society_registration.description,
                society_type=society_registration.society_type,
                status="pending",  # Ensure it's pending so admin can see it
                manager=society_registration.applicant,
                visibility="Private",  # Admin should still see private ones
            )
            new_society.save()

            # Create a membership for the manager with manager role
            Membership.objects.create(
                society=new_society,
                user=request.user,
                role=MembershipRole.MANAGER,
                status=MembershipStatus.APPROVED
            )

            # messages.success(request, "Society application submitted. Awaiting approval.")
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
    return render(request, 'admin_pending_societies.html', {
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
                society.visibility = 'Public'
                society.save()
                # messages.success(request, f"Society '{society.name}' has been approved and set to private.")
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

@login_required
def view_manage_societies(request):
    if request.user.is_superuser:
        # For admin users, show all societies regardless of status
        societies = Society.objects.all()
    else:
        # For regular users, show only approved societies
        societies = Society.objects.filter(status='approved')

    news_list = News.objects.filter(is_published=True).order_by('-date_posted')[:10]
    return render(request, "societies.html", {
        'societies': societies,
        'news_list': news_list,
        'page': 'Manage'
    })

@login_required
def manage_society(request, society_id):
    """
    Display a page listing all current Membership objects for this society.
    Only the manager or co_manager may view this page.
    """
    society = get_object_or_404(Society, id=society_id)

    # Check if request.user is the manager (the one who created the society):
    if request.user.is_superuser:
        is_authorized = True

    else:
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

    society.members_count = Membership.objects.filter(
        society=society,
        status=MembershipStatus.APPROVED
    ).count()
    society.save()


    # Get all memberships for this society
    memberships = Membership.objects.filter(society=society).select_related('user')

    return render(request, 'manage_society.html', {
        'society': society,
        'memberships': memberships,
        'user' : request.user,
        'members_count': society.members_count
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
    if society.manager != request.user:
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
            # messages.success(request, f"{membership.user.email} has been approved!")

        elif action == 'remove':
            # Remove the membership entirely
            membership.delete()
            # messages.success(request, f"{membership.user.email} has been removed from {society.name}.")

        elif action == 'promote_co_manager':
            membership.role = MembershipRole.CO_MANAGER
            membership.status = MembershipStatus.APPROVED  # ensure approved
            membership.save()
            # messages.success(request, f"{membership.user.email} is now a Co-Manager.")

        elif action == 'promote_editor':
            membership.role = MembershipRole.EDITOR
            membership.status = MembershipStatus.APPROVED
            membership.save()
            # messages.success(request, f"{membership.user.email} is now an Editor.")

        else:
            messages.error(request, "Invalid action.")
            return redirect('manage_society', society_id=society.id)

        society.members_count = Membership.objects.filter(
            society=society,
            status=MembershipStatus.APPROVED
        ).count()
        society.save()

        return redirect('manage_society', society_id=society_id)

    else:
        return render(request, 'update_membership.html', {
            'society': society,
            'membership': membership
            }
        )

@login_required
def join_society(request, society_id):
    """Display the join form for a society and handle submission."""
    society = get_object_or_404(Society, id=society_id)

    # Check if user is already in the membership table with an approved or pending status
    existing_member = Membership.objects.filter(society=society, user=request.user).first()

    if existing_member and existing_member.status in [MembershipStatus.APPROVED, MembershipStatus.PENDING]:
        messages.info(request, "You are already a member or have an application pending.")
        return redirect('society_page', society_id=society.id)

    requirement = getattr(society, 'requirement', None)
    req_type = requirement.requirement_type if requirement else RequirementType.NONE

    if req_type == RequirementType.NONE:
        if society.joining_fee > 0:
             return render(request, "confirm_join_payment.html", {"society": society})
        if request.method == 'POST':

            form = JoinSocietyForm(society=society, user=request.user, data=request.POST, files=request.FILES)
            if form.is_valid():
                application = form.create_membership_and_application()
                if application.is_approved:
                    pass
                    # messages.success(request, "You have joined the society successfully!")
                return redirect('society_page', society_id=society.id)
            else:
                return render(request, 'join_society.html', {'society': society, 'form': form})

        else:
            form = JoinSocietyForm(society=society, user=request.user)

            return render(request, 'join_society.html', {
                'society': society,
                'form': form,
                'auto_approve': True
            })
    else:
        if request.method == 'POST':
            form = JoinSocietyForm(society=society, user=request.user, data=request.POST, files=request.FILES)
            if form.is_valid():
                application = form.create_membership_and_application()
                if application.is_approved:
                    pass
                    # messages.success(request, "You have joined the society successfully!")
                elif application.is_rejected:
                    messages.error(request, "Your application was rejected based on your answers.")
                else:
                    messages.info(request, "Your application has been submitted and is pending approval.")
                return redirect('society_page', society_id=society.id)
            else:
                return render(request, 'join_society.html', {'society': society, 'form': form})
        else:
            form = JoinSocietyForm(society=society, user=request.user)
            return render(request, 'join_society.html', {
                'society': society,
                'form': form,
                'auto_approve': False
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
    from .models import MembershipApplication, MembershipRole
    """Manager or co-manager can approve or reject an application with requirement_type=manual."""
    society = get_object_or_404(Society, id=society_id)
    application = get_object_or_404(society.applications, id=application_id)
    # same manager check
    # is_manager_or_co = False
    # if society.manager == request.user:
    #     is_manager_or_co = True
    # else:
    #     membership_co = Membership.objects.filter(
    #         society=society,
    #         user=request.user,
    #         role=MembershipRole.CO_MANAGER,
    #         status=MembershipStatus.APPROVED
    #     ).first()
    #     is_manager_or_co = bool(membership_co)

    is_manager_or_co = (society.manager == request.user) or Membership.objects.filter(
        society=society,
        user=request.user,
        role=MembershipRole.CO_MANAGER,
        status=MembershipStatus.APPROVED
    ).exists()

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
            defaults={'role': MembershipRole.MEMBER, 'status': MembershipStatus.APPROVED}
        )

        # Now update status to approved
        membership.status = MembershipStatus.APPROVED
        membership.save()
        # messages.success(request, f"Application for {application.user.email} approved.")

    elif decision == 'reject':
        application.is_rejected = True
        application.save()

        # remove membership (if it exists):
        Membership.objects.filter(society=society, user=application.user).delete()
        messages.warning(request, f"Application for {application.user.email} rejected.")

    # get all the society type
    # society_types = Society.objects.values_list('society_type', flat=True).distinct()

    # a dictionary to start top societies
    # top_societies_per_type = {}
    # print("All Societies:", list(Society.objects.all()))

    # all_approved_societies = approved_societies(request.user)

    # for society_type, _ in SOCIETY_TYPE_CHOICES:
    #     top_societies_per_type[society_type] = (
    #         all_approved_societies.filter(society_type=society_type)
    #         .order_by('-members_count')[:5]
    #     )
    #     membership.status = MembershipStatus.APPROVED
    #     membership.save()
    #     messages.success(request, f"Application for {application.user.email} approved.")
    # else:
    #     application.is_rejected = True
    #     application.save()
    #     # remove membership if any
    #     Membership.objects.filter(society=society, user=application.user).delete()
    #     messages.warning(request, f"Application for {application.user.email} rejected.")


    return redirect('view_applications', society_id=society.id)



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
            # messages.success(request, "Your society was automatically deleted.")

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
            # messages.success(request, f"Society '{society.name}' has been deleted.")
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
        # messages.success(request, f"{widget_type} widget added!")

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
    # messages.success(request, "Widget removed successfully.")
    return redirect("society_admin_view", society_id=society_id)

def society_page(request, society_id):
    society = get_object_or_404(Society, id=society_id)
    widgets = Widget.objects.filter(society=society).order_by("position")

    members_count = Membership.objects.filter(
        society=society,
        status=MembershipStatus.APPROVED
    ).count()

    membership = None
    is_member = False
    is_manager = False

    if request.user.is_authenticated:
        membership = Membership.objects.filter(society=society, user=request.user).first()
        if membership and membership.status == 'approved':
            is_member = True
        if society.manager == request.user:
            is_manager = True

    context = {
        "society": society,
        "widgets": widgets,
        "membership": membership,
        "user_membership": membership,
        "is_member": is_member,
        "is_manager": is_manager,
        "members_count": members_count,
    }
    return render(request, "society_page.html", context)


@login_required
def leave_society(request, society_id):
    society = get_object_or_404(Society, id=society_id)
    membership = Membership.objects.filter(
        society=society,
        user=request.user,
        status=MembershipStatus.APPROVED
    ).first()

    if not membership:
        messages.error(request, "You are not an approved member of this society.")
        return redirect('society_page', society_id=society.id)

    if request.method == "POST":
        # user confirmed
        membership.delete()
        # messages.success(request, f"You have left '{society.name}'.")
        return redirect('society_page', society_id=society.id)

    return render(request, "confirm_leave.html", {"society": society})

@login_required
def manage_display(request, society_id):
    society = get_object_or_404(Society, id=society_id)

    if request.user != society.manager:
        membership = Membership.objects.filter(
            society=society,
            user=request.user,
            status=MembershipStatus.APPROVED
        ).first()
        if not membership or (membership.role not in [MembershipRole.CO_MANAGER, MembershipRole.EDITOR] and not user.is_superuser):
            messages.error(request, "You do not have permission to manage widget display for this society.")
            return redirect("society_page", society_id=society.id)

    if request.method == "POST":
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
                widget_order = data.get("widget_order")
                if widget_order:
                    for index, widget_id in enumerate(widget_order):
                        widget = Widget.objects.get(id=widget_id, society=society)
                        widget.position = index
                        widget.save()
                    return JsonResponse({"status": "success", "message": "Widget order updated."})
                else:
                    return JsonResponse({"status": "error", "message": "No widget order provided."}, status=400)
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=400)
        else:
            widget_type = request.POST.get("widget_type")
            if widget_type:
                new_position = Widget.objects.filter(society=society).count()
                Widget.objects.create(society=society, widget_type=widget_type, position=new_position)
                messages.success(request, f"Added new widget of type '{widget_type}'.")
                return redirect("manage_display", society_id=society.id)

    widgets = Widget.objects.filter(society=society).order_by("position")
    return render(request, "manage_display.html", {"society": society, "widgets": widgets})
