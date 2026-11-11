from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem, DELIVERY_CHOICES, DELIVERY_RATES
from .utils import get_or_create_cart
from decimal import Decimal

def cart_detail_view(request):
    cart = get_or_create_cart(request)
    
    # Handle delivery option change if submitted via POST
    if request.method == "POST" and "delivery_option" in request.POST:
        chosen_option = request.POST.get("delivery_option")
        if chosen_option in DELIVERY_RATES:
            cart.delivery_option = chosen_option
            cart.save()
            messages.success(request, f"Delivery method updated to {cart.delivery_label}.")
            return redirect("cart_detail")

    # Prepare delivery choices with current pricing and badges
    delivery_options_data = []
    for code, label in DELIVERY_CHOICES:
        rate = DELIVERY_RATES[code]
        price = rate["price"]
        threshold = rate["free_threshold"]
        
        is_free = False
        if threshold and cart.subtotal >= threshold:
            price = Decimal("0.00")
            is_free = True

        delivery_options_data.append({
            "code": code,
            "label": label,
            "price": price,
            "is_free": is_free,
            "free_threshold": threshold,
            "is_selected": cart.delivery_option == code,
        })

    return render(
        request,
        "cart/cart_detail.html",
        {
            "cart": cart,
            "delivery_options": delivery_options_data,
        },
    )


@require_POST
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request)

    try:
        quantity = int(request.POST.get("quantity", 1))
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": 0})
    
    new_quantity = cart_item.quantity + quantity
    if new_quantity > product.stock:
        cart_item.quantity = product.stock
        cart_item.save()
        messages.warning(request, f"Added maximum available stock ({product.stock}) for {product.title}.")
    else:
        cart_item.quantity = new_quantity
        cart_item.save()
        messages.success(request, f"Added {product.title} to your cart!")

    # Redirect back to where the user clicked, or to cart if specified
    redirect_to = request.POST.get("next") or request.META.get("HTTP_REFERER") or "cart_detail"
    return redirect(redirect_to)


@require_POST
def update_cart_item_view(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    action = request.POST.get("action")

    if action == "increase":
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, f"Maximum available stock for {cart_item.product.title} reached.")
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, f"Removed {cart_item.product.title} from your cart.")
            return redirect("cart_detail")
    elif action == "set":
        try:
            qty = int(request.POST.get("quantity", 1))
            if qty <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = min(qty, cart_item.product.stock)
                cart_item.save()
        except ValueError:
            pass

    return redirect("cart_detail")


@require_POST
def remove_cart_item_view(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    title = cart_item.product.title
    cart_item.delete()
    messages.info(request, f"Removed {title} from your cart.")
    return redirect("cart_detail")
