from django.shortcuts import render
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from apps.widgets.models import Widget
from apps.societies.models import Society

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

def remove_widget(request, widget_id):
    widget = get_object_or_404(Widget, id=widget_id)
    society = widget.society
    if request.user != society.manager:
        return JsonResponse({"error": "Permission denied"}, status=403)
    widget.delete()
    return JsonResponse({"success": True})