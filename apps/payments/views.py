import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from apps.societies.models import Society
from apps.events.models import Event
from apps.payments.models import Payment
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        name = request.POST.get("name")
        price = float(request.POST.get("price", 0)) * 100  # Convert to cents
        description = request.POST.get("description")

        if not event_id or not name or not price:
            return JsonResponse({"error": "Event ID is missing!"}, status=400)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card, apple pay, google pay"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": name,
                                "description": description,
                            },
                            "unit_amount": int(price),
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url="http://127.0.0.1:8000/payments/success/",
                cancel_url="http://127.0.0.1:8000/payments/cancel/",
            )

            return JsonResponse({"url": session.url})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def payment_success(request):
    """Handles successful payments."""
    return render(request, "payment_success.html")

def payment_cancel(request):
    """Handles cancelled payments."""
    return render(request, "payment_cancel.html")