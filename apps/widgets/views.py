from django.shortcuts import render
from django.contrib import messages
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Widget
from .forms import *
from apps.societies.models import Society, Membership, MembershipRole, MembershipStatus
import json

@csrf_exempt
def update_widget_order(request, society_id):
    """AJAX endpoint to update the order of widgets."""
    if request.method == "POST":
        society = get_object_or_404(Society, id=society_id)
        # Ensure only the manager can update the order.
        if request.user != society.manager:
            return JsonResponse({"error": "Permission denied"}, status=403)
        try:
            data = json.loads(request.body)
            widget_order = data.get("widget_order", [])
            for index, widget_id in enumerate(widget_order):
                widget = get_object_or_404(Widget, id=widget_id, society=society)
                widget.position = index
                widget.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

def remove_widget(request, society_id, widget_id):
    widget = get_object_or_404(Widget, id=widget_id)
    society = widget.society
    
    # fetch the user's membership
    membership = Membership.objects.filter(
        society=society,
        user=request.user,
        status=MembershipStatus.APPROVED
    ).first()
    
    is_authorized = False
    
    if request.user == society.manager:
        is_authorized = True
    else:
        if membership and membership.role in [MembershipRole.CO_MANAGER, MembershipRole.EDITOR]:
            is_authorized = True
    
    if not is_authorized:
        return JsonResponse({"error": "Permission denied"}, status=403)
    
    widget.delete()
    return JsonResponse({"success": True})

def edit_contact_widget(request, society_id, widget_id):
    """Allows manager to add/remove contact information for the society."""
    widget = get_object_or_404(
        Widget, id=widget_id, society__id=society_id, widget_type='contacts'
    )
    initial_data = widget.data if widget.data else {}
    
    if request.method == "POST":
        form = ContactWidgetForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the cleaned data as JSON in widget.data
            widget.data = form.cleaned_data
            widget.save()
            messages.success(request, "Contact information updated successfully!")
            return redirect("manage_display", society_id=society_id)
        else:
            messages.error(request, "There was an error updating the contact information.")
    else:
        form = ContactWidgetForm(initial=initial_data)
    
    return render(request, "edit_contact_widget.html", {
        "form": form,
        "widget": widget,
        "society_id": society_id,
    })
    
def edit_featured_members_widget(request, society_id, widget_id):
    """Allows managers to edit the "featured" widget by adding multiple featured members."""
    widget = get_object_or_404(Widget, id=widget_id, society__id=society_id, widget_type='featured')
    FeaturedMemberFormSet = formset_factory(FeaturedMemberForm, extra=1)
    
    initial_data = widget.data.get('featured_members', []) if widget.data else []
    
    if request.method == "POST":
        formset = FeaturedMemberFormSet(request.POST, request.FILES)
        if formset.is_valid():
            featured_members = []
            for form in formset:
                if form.cleaned_data and (form.cleaned_data.get('name') or form.cleaned_data.get('role')):
                    picture_field = form.cleaned_data.get('picture')
                    picture_url = picture_field.url if picture_field else ""
                    featured_members.append({
                        'name': form.cleaned_data.get('name'),
                        'role': form.cleaned_data.get('role'),
                        'picture': picture_url,
                    })
            if widget.data is None:
                widget.data = {}
            widget.data['featured_members'] = featured_members
            widget.save()
            messages.success(request, "Featured members updated successfully!")
            return redirect("manage_display", society_id=society_id)
        else:
            messages.error(request, "There was an error updating featured members.")
    else:
        formset = FeaturedMemberFormSet(initial=initial_data)
    
    return render(request, "edit_featured_members_widget.html", {
        "formset": formset,
        "widget": widget,
        "society_id": society_id,
    })
    
def edit_announcements_widget(request, society_id, widget_id):
    """Allows managers to make announcements."""
    widget = get_object_or_404(Widget, id=widget_id, society__id=society_id, widget_type='announcements')
    AnnouncementFormSet = formset_factory(AnnouncementForm, extra=1)
    initial_data = widget.data.get('announcements', []) if widget.data else []
    
    if request.method == "POST":
        formset = AnnouncementFormSet(request.POST)
        if formset.is_valid():
            announcements = []
            for form in formset:
                if form.cleaned_data and form.cleaned_data.get('title'):
                    announcements.append({
                        'title': form.cleaned_data.get('title'),
                        'message': form.cleaned_data.get('message'),
                        'date': str(form.cleaned_data.get('date')) if form.cleaned_data.get('date') else "",
                    })
            if widget.data is None:
                widget.data = {}
            widget.data['announcements'] = announcements
            widget.save()
            messages.success(request, "Announcements updated successfully!")
            return redirect("manage_display", society_id=society_id)
        else:
            messages.error(request, "There was an error updating the announcements.")
    else:
        formset = AnnouncementFormSet(initial=initial_data)
    
    return render(request, "edit_announcements_widget.html", {
        "formset": formset,
        "widget": widget,
        "society_id": society_id,
    })
    
def edit_leaderboard_widget(request, society_id, widget_id):
    """Allows managers to update leaderboard points for each member and toggle whether to display points."""
    widget = get_object_or_404(Widget, id=widget_id, society__id=society_id, widget_type='leaderboard')
    society = widget.society

    # get all approved memberships for the society
    memberships = Membership.objects.filter(society=society, status=MembershipStatus.APPROVED)

    initial_points = {}
    display_points = True
    display_count = '3'
    if widget.data:
        initial_points = widget.data.get('points', {})
        display_points = widget.data.get('display_points', True)
        display_count = str(widget.data.get('display_count', '3'))

    LeaderboardFormSet = formset_factory(LeaderboardMembershipForm, extra=0)
    initial_data = []
    for membership in memberships:
        full_name = membership.user.get_full_name() if hasattr(membership.user, "get_full_name") else str(membership.user)
        initial_data.append({
            'membership_id': membership.id,
            'member_name': full_name,
            'points': initial_points.get(str(membership.id), 0),
        })

    if request.method == "POST":
        formset = LeaderboardFormSet(request.POST, prefix='members')
        settings_form = LeaderboardSettingsForm(request.POST, prefix='settings')
        if formset.is_valid() and settings_form.is_valid():
            new_points = {}
            for form in formset:
                mid = form.cleaned_data.get('membership_id')
                pts = form.cleaned_data.get('points', 0)
                new_points[str(mid)] = pts
            widget.data = {
                'points': new_points,
                'display_points': settings_form.cleaned_data.get('display_points', False),
                'display_count': int(settings_form.cleaned_data.get('display_count'))
            }
            widget.save()
            messages.success(request, "Leaderboard updated successfully!")
            return redirect("manage_display", society_id=society_id)
        else:
            messages.error(request, "There was an error updating the leaderboard.")
    else:
        formset = LeaderboardFormSet(initial=initial_data, prefix='members')
        settings_form = LeaderboardSettingsForm(
            initial={'display_points': display_points, 'display_count': display_count},
            prefix='settings'
        )
    
    return render(request, "edit_leaderboard_widget.html", {
        "formset": formset,
        "settings_form": settings_form,
        "widget": widget,
        "society": society,
    })