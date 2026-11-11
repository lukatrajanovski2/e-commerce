from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.utils import get_or_create_cart
from .models import Order, OrderItem
from .forms import CheckoutForm

def checkout_view(request):
    cart = get_or_create_cart(request)
    if cart.item_count == 0:
        messages.warning(request, "Your cart is empty. Add products before checking out!")
        return redirect("home")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.delivery_option = cart.delivery_label
            order.delivery_fee = cart.delivery_fee
            order.subtotal = cart.subtotal
            order.grand_total = cart.grand_total
            order.save()

            # Create OrderItems & decrement stock
            for item in cart.items.select_related("product"):
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_title=item.product.title,
                    price=item.product.price,
                    quantity=item.quantity,
                )
                # Decrement product stock safely
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                    item.product.save()

            # Clear cart
            cart.items.all().delete()
            messages.success(request, f"Order #{order.id} placed successfully! Thank you for your purchase.")
            return redirect("order_success", order_id=order.id)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                "full_name": f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                "email": request.user.email,
            }
        form = CheckoutForm(initial=initial_data)

    return render(
        request,
        "orders/checkout.html",
        {
            "form": form,
            "cart": cart,
        },
    )


def order_success_view(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id)
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items").order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})
