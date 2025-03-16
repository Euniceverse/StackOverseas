import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from apps.societies.models import Society
from apps.events.models import Event
from apps.payments.models import Payment
from django.shortcuts import render

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request):
    """Handles payment for either society membership or event registration and redirects to Stripe Checkout."""
    item_type = request.GET.get("type") 
    item_id = request.GET.get("id")  

    if item_type == "society":
        society = get_object_or_404(Society, id=item_id)
        amount = 200  # in pence
        description = f"Membership for {society.name}"
    elif item_type == "event":
        event = get_object_or_404(Event, id=item_id)
        amount = int(event.fee * 100)  # convert to pence
        description = f"Entry to {event.name}"
    else:
        return redirect("payment_error")  

    # create checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "gbp",
                "product_data": {"name": description},
                "unit_amount": amount,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{settings.DOMAIN_NAME}/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.DOMAIN_NAME}/payments/cancel",
    )

   # store in DB
    Payment.objects.create(
        user=request.user,
        amount=amount / 100,
        status="pending",
        stripe_charge_id=session.id,
        payment_for=item_type,
    )

    return redirect(session.url)
def payment_success(request):
    """Handles successful payments."""
    return render(request, "payments/payment_success.html")

def payment_cancel(request):
    """Handles cancelled payments."""
    return render(request, "payments/payment_cancel.html")