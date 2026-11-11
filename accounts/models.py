from django.db import models
from django.contrib.auth.models import User

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    store_name = models.CharField(max_length=120, unique=True)
    bio = models.TextField(blank=True, help_text="Short description about the seller or store")
    phone_number = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.store_name} ({self.user.username})"

# Convenience method for User
def is_seller(self):
    return hasattr(self, "seller_profile")

User.add_to_class("is_seller", property(is_seller))
