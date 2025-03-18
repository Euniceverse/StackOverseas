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
from .models import Event


stripe.api_key = settings.STRIPE_SECRET_KEY

# def create_checkout_session(request):
#     """Handles payment for either society membership or event registration and redirects to Stripe Checkout."""
#     item_type = request.GET.get("type") 
#     item_id = request.GET.get("id")  

#     print(f"DEBUG: item_type={item_type}, item_id={item_id}") 

#     if not item_id or not item_id.isdigit():  # ✅ Validate item_id
#         return HttpResponseBadRequest("Invalid or missing item ID")  

#     item_id = int(item_id)  # ✅ Convert to integer after validation

#     if item_type == "society":
#         society = get_object_or_404(Society, id=item_id)
#         amount = 200  # in pence
#         description = f"Membership for {society.name}"
#     elif item_type == "event":
#         event = get_object_or_404(Event, id=item_id)
#         amount = int(event.fee * 100)  # convert to pence
#         description = f"Entry to {event.name}"
#     else:
#         return HttpResponseBadRequest("Invalid item type")

#     # create checkout session
#     session = stripe.checkout.Session.create(
#         payment_method_types=["card"],
#         line_items=[{
#             "price_data": {
#                 "currency": "gbp",
#                 "product_data": {"name": description},
#                 "unit_amount": amount,
#             },
#             "quantity": 1,
#         }],
#         mode="payment",
#         success_url="http://127.0.0.1:8000/payments/success",  # ✅ Replace with a working URL

#         #success_url=f"{settings.DOMAIN_NAME}/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
#         cancel_url=f"{settings.DOMAIN_NAME}/payments/cancel",
#     )

#    # store in DB
#     Payment.objects.create(
#         user=request.user,
#         amount=amount / 100,
#         status="pending",
#         stripe_charge_id=session.id,
#         payment_for=item_type,
#     )

#     return redirect(session.url)

# def create_checkout_session(request):
#     """Handles payment for either society membership or event registration and redirects to Stripe Checkout."""
#     item_type = request.GET.get("type") 
#     item_id = request.GET.get("id")  

#     if not item_id or not item_id.isdigit():  
#         return JsonResponse("Invalid or missing item ID")  

#     item_id = int(item_id)  

#     if item_type == "event":
#         event = get_object_or_404(Event, id=item_id)
#         amount = int(float(event.fee) * 100)
#         description = f"Event registration for {event.name}"

#         if amount <= 0:
#             return JsonResponse({"error": "Invalid amount. Must be greater than zero."}, status=400)

#         description = f"Registration for {event.name}"

#     else:
#         return JsonResponse("Invalid type")

#     success_url = f"http://127.0.0.1:8000/payments/success?session_id={{CHECKOUT_SESSION_ID}}"
#     cancel_url = f"http://127.0.0.1:8000/payments/cancel"

#     print(f"✅ DEBUG: success_url={success_url}")  
#     print(f"✅ DEBUG: cancel_url={cancel_url}")  

#     try:
#         session = stripe.checkout.Session.create(
#             payment_method_types=["card"],
#             line_items=[
#                 {
#                     "price_data": {
#                         "currency": "gbp",
#                         "product_data": {
#                             "name": description,
#                         },
#                         "unit_amount": amount,
#                     },
#                     "quantity": 1,
#                 }
#             ],
#             mode="payment",
#             success_url = f"http://127.0.0.1:8000/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
#             cancel_url = f"http://127.0.0.1:8000/payments/cancel",
#         )
#         return JsonResponse({"sessionId": session.id})
    
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

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
                payment_method_types=["card"],
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

            return JsonResponse({"sessionId": session.id})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def payment_success(request):
    """Handles successful payments."""
    return render(request, "payment_success.html")

def payment_cancel(request):
    """Handles cancelled payments."""
    return render(request, "payment_cancel.html")