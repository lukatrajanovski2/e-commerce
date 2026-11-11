from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from products.models import Product

DELIVERY_CHOICES = [
    ("standard", "Standard Shipping (3-5 business days)"),
    ("express", "Express Shipping (1-2 business days)"),
    ("same_day", "Same-Day Courier Delivery"),
    ("pickup", "Free In-Store / Warehouse Pickup"),
]

DELIVERY_RATES = {
    "standard": {"price": Decimal("4.99"), "free_threshold": Decimal("50.00"), "label": "Standard Delivery (3-5 days)"},
    "express": {"price": Decimal("12.99"), "free_threshold": None, "label": "Express Delivery (1-2 days)"},
    "same_day": {"price": Decimal("19.99"), "free_threshold": None, "label": "Same-Day Courier"},
    "pickup": {"price": Decimal("0.00"), "free_threshold": None, "label": "Store Pickup"},
}

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="carts")
    session_key = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default="standard")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Cart #{self.id} (User: {self.user or self.session_key})"

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def delivery_fee(self):
        config = DELIVERY_RATES.get(self.delivery_option, DELIVERY_RATES["standard"])
        fee = config["price"]
        threshold = config["free_threshold"]
        if threshold is not None and self.subtotal >= threshold:
            return Decimal("0.00")
        return fee

    @property
    def grand_total(self):
        return self.subtotal + self.delivery_fee

    @property
    def delivery_label(self):
        config = DELIVERY_RATES.get(self.delivery_option, DELIVERY_RATES["standard"])
        return config["label"]


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity}x {self.product.title}"

    @property
    def total_price(self):
        return self.product.price * self.quantity
