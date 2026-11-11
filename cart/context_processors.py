from cart.utils import get_or_create_cart

def cart_context(request):
    try:
        cart = get_or_create_cart(request)
        return {
            "global_cart": cart,
            "cart_item_count": cart.item_count,
        }
    except Exception:
        return {
            "global_cart": None,
            "cart_item_count": 0,
        }

