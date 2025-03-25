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
        payment_type = request.POST.get("type")  # 'event' or 'society'

        if payment_type == "event":
            event_id = request.POST.get("id")
            name = request.POST.get("name")
            price = float(request.POST.get("price", 0)) * 100
            description = request.POST.get("description")

            success_url = f"https://{settings.DOMAIN_NAME}/payments/success/?event_id={event_id}"
        
        elif payment_type == "society":
            society_id = request.POST.get("id")
            name = request.POST.get("name")
            price = float(request.POST.get("price", 0)) * 100
            description = request.POST.get("description")

           
            success_url = f"https://{settings.DOMAIN_NAME}/payments/success/?type=society&id={society_id}"

        else:
            return JsonResponse({"error": "Invalid payment type"}, status=400)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {
                            "name": name,
                            "description": description,
                        },
                        "unit_amount": int(price),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=f"https://{settings.DOMAIN_NAME}/payments/cancel/?type={payment_type}&id={request.POST.get('id')}",
            )

            if payment_type == "society":
                return redirect( session.url)
            else:
                return JsonResponse({"url": session.url})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



def payment_success(request):
    object_type = request.GET.get("type")
    object_id = request.GET.get("id")
    return render(request, "payment_success.html", {"type": object_type, "id": object_id})


def payment_cancel(request):
    object_type = request.GET.get("type")  # 'event' or 'society'
    object_id = request.GET.get("id")

    try:
        object_id = int(object_id)
        if object_type == "event":
            obj = get_object_or_404(Event, id=object_id)
        elif object_type == "society":
            obj = get_object_or_404(Society, id=object_id)
        else:
            obj = None
    except (ValueError, TypeError):
        obj = None

    return render(request, "payment_cancel.html", {"object": obj, "type": object_type})