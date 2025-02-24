'''for society functions'''
from .models import Society
from apps.users.models import CustomUser
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


# def top_societies():
#     """View to show top 5 societies per type and overall"""
#     from .models import SOCIETY_TYPE_CHOICES  

#     # dic to store top societies per type
#     top_societies_per_type = {}

#     all_approved_societies = approved_socities()

#     for society_type, _ in SOCIETY_TYPE_CHOICES:
#         top_societies_per_type[society_type] = (
#             all_approved_societies.filter(society_type=society_type)
#             .order_by('-members_count')[:5]
#         )

#     top_overall_societies = all_approved_societies.order_by('-members_count')[:5]

#     return {
#         'top_overall_societies': top_overall_societies,
#         'top_societies_per_type': top_societies_per_type
#     }

def top_societies():
    """Fetch top 5 societies overall and per type."""
    approved_societies = Society.objects.filter(status="approved")
    
    # Top 5 overall
    top_overall_societies = approved_societies.order_by('-members_count')[:5]

    # Top 5 per type
    top_societies_per_type = {}
    for society_type, _ in SOCIETY_TYPE_CHOICES:
        top_societies_per_type[society_type] = (
            approved_societies.filter(society_type=society_type)
            .order_by('-members_count')[:5]
        )

    return {
        "top_overall_societies": top_overall_societies,
        "top_societies_per_type": top_societies_per_type
    }