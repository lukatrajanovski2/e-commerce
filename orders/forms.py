from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["full_name", "email", "phone", "shipping_address", "city", "postal_code"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Jane Doe", "class": "input-field"}),
            "email": forms.EmailInput(attrs={"placeholder": "jane@example.com", "class": "input-field"}),
            "phone": forms.TextInput(attrs={"placeholder": "+1 (555) 123-4567", "class": "input-field"}),
            "shipping_address": forms.Textarea(attrs={"placeholder": "Street address, apartment, suite, etc.", "rows": 3, "class": "input-field"}),
            "city": forms.TextInput(attrs={"placeholder": "City / Metro", "class": "input-field"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "Zip or postal code", "class": "input-field"}),
        }

