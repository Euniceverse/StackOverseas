from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Widget
from .forms import ContactWidgetForm
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