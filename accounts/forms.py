from django import forms
from django.contrib.auth.models import User
from .models import SellerProfile

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Enter password", "class": "input-field"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm password", "class": "input-field"}))

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Choose a username", "class": "input-field"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "class": "input-field"}),
            "first_name": forms.TextInput(attrs={"placeholder": "First name", "class": "input-field"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name", "class": "input-field"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("password")
        pwd_confirm = cleaned_data.get("confirm_password")
        if pwd and pwd_confirm and pwd != pwd_confirm:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data


class SellerOnboardingForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ["store_name", "phone_number", "bio"]
        widgets = {
            "store_name": forms.TextInput(attrs={"placeholder": "e.g. Nordic Trends, Apex Tech", "class": "input-field"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+1 (555) 000-0000", "class": "input-field"}),
            "bio": forms.Textarea(attrs={"placeholder": "Describe what you sell and your store story...", "rows": 3, "class": "input-field"}),
        }

