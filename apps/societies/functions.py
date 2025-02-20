'''for society functions'''
from .models import Society
from apps.users.models import CustomUser

def approved_socities():
    return Society.objects.filter(status="approved")

def get_societies(user):
    """Get all approved societies where the given user is a member."""
    if CustomUser.objects.filter(pk=user.pk).exists():
        return Society.objects.filter(status="approved", members=user)
    return approved_socities()

def manage_societies():
    return Society.objects.filter(status__in=['pending','request_delete'])

