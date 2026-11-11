from cart.models import Cart

def get_or_create_cart(request):
    """
    Returns the active cart for the current request.
    Handles both logged in users and anonymous session visitors.
    If an anonymous user logs in, merges their session cart.
    """
    if not request.session.session_key:
        request.session.save()

    session_key = request.session.session_key

    if request.user.is_authenticated:
        # Check if user has an existing cart
        user_cart = Cart.objects.filter(user=request.user).first()
        session_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()

        if session_cart and not user_cart:
            session_cart.user = request.user
            session_cart.save()
            return session_cart
        elif session_cart and user_cart:
            # Merge session cart items into user cart
            for item in session_cart.items.all():
                existing = user_cart.items.filter(product=item.product).first()
                if existing:
                    existing.quantity += item.quantity
                    existing.save()
                else:
                    item.cart = user_cart
                    item.save()
            session_cart.delete()
            return user_cart
        elif user_cart:
            return user_cart
        else:
            return Cart.objects.create(user=request.user)
    else:
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
        return cart

