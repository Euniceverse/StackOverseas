from django import template

register = template.Library()

@register.filter
def get_user_membership(memberships, user):
    """
    Returns the membership object for the given user, or None if not found.
    Usage in template:
        {% with my_membership=society.society_memberships.all|get_user_membership:user %}
          ...
        {% endwith %}
    """
    return memberships.filter(user=user).first()
