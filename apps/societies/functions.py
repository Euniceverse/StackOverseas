'''for society functions'''
from .models import Society, Membership, SocietyRegistration
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from apps.users.models import CustomUser
from django import template
from config.constants import SOCIETY_TYPE_CHOICES


def staff_required(user):
    return user.is_staff

def approved_societies(user):
    if user.is_superuser:
        return Society.objects.all()
    return Society.objects.filter(status="approved")

def get_societies(user):
    """Get all approved societies where the given user is a member."""

    # Check if the user exists
    if not CustomUser.objects.filter(pk=user.pk).exists():
        return approved_societies()  # Fallback if user doesn't exist

    # Query societies managed by the user
    managing_societies = Society.objects.filter(manager_id=user.id)
    
    # Query approved societies where the user is a member
    member_societies = Society.objects.filter(status="approved", members=user)

    if managing_societies.exists():
        # The union (|) operator combines two QuerySets and removes duplicates
        return (managing_societies | member_societies).distinct()

    
    return member_societies


def manage_societies():
    return Society.objects.filter(status__in=['pending','request_delete'])


def get_all_users():
    # return CustomUser.objects.filter(is_superuser = False)
    return Membership.objects.all()


register = template.Library()

@register.filter
def get_user_membership(all_memberships, user):
    """
    Usage in template:
      {% with my_membership=society.society_memberships.all|get_user_membership:user %}
        ...
      {% endwith %}
    Returns the membership object for the given user, or None if not found.
    """
    return all_memberships.filter(user=user).first()


def top_societies(user):
    """Return a dict with top societies per type and top overall societies."""
    top_societies_per_type = {}
    all_approved = approved_societies(user)

    for society_type, _ in SOCIETY_TYPE_CHOICES:
        top_societies_per_type[society_type] = (
            all_approved.filter(society_type=society_type).order_by('-members_count')[:5]
        )

    top_overall_societies = Society.objects.order_by('-members_count')[:5]

    return {
        'top_overall_societies': top_overall_societies,
        'top_societies_per_type': top_societies_per_type
    }

@user_passes_test(staff_required)
def approve_society(request, registration_id):
    """Approve a society registration and create the actual Society."""
    registration = get_object_or_404(SocietyRegistration, id=registration_id, status='pending')
    
    # create the society from the approved registration
    new_society = Society.objects.create(
        name=registration.name,
        description=registration.description,
        society_type=registration.society_type,
        manager=registration.applicant, 
        status='approved',
        visibility=registration.visibility
    )
    
    messages.success(request, f"Society '{society.name}' has been approved and created!")
    return redirect("admin_society_list")