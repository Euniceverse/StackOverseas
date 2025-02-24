'''for society functions'''
from .models import Society
from apps.users.models import CustomUser
from django import template
from config.constants import SOCIETY_TYPE_CHOICES

def approved_socities():
    return Society.objects.filter(status="approved")

def get_societies(user):
    """Get all approved societies where the given user is a member."""
    if CustomUser.objects.filter(pk=user.pk).exists():
        return Society.objects.filter(status="approved", members=user)
    return approved_socities()


def manage_societies():
    return Society.objects.filter(status__in=['pending','request_delete'])


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


def top_societies():
    """Return a dict with top societies per type and top overall societies."""
    top_societies_per_type = {}
    all_approved = approved_socities()

    for society_type, _ in SOCIETY_TYPE_CHOICES:
        top_societies_per_type[society_type] = (
            all_approved.filter(society_type=society_type).order_by('-members_count')[:5]
        )

    top_overall_societies = Society.objects.order_by('-members_count')[:5]

    return {
        'top_overall_societies': top_overall_societies,
        'top_societies_per_type': top_societies_per_type
    }

