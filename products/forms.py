from django import forms
from .models import Product, Category
from decimal import Decimal, InvalidOperation

class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="-- Select Category or Subcategory --",
        widget=forms.Select(attrs={"class": "input-field font-medium cursor-pointer"}),
        required=True,
    )
    stock = forms.IntegerField(
        initial=1,
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={"placeholder": "e.g. 10", "min": "0", "class": "input-field"}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "placeholder": "Describe features, dimensions, condition, specifications...",
            "rows": 4,
            "class": "input-field",
        }),
    )
    price = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "29.99",
            "class": "input-field pl-7",
            "inputmode": "decimal",
        }),
        help_text="Item price in USD (e.g. 29.99)",
    )

    class Meta:
        model = Product
        fields = ["title", "category", "price", "stock", "description", "image", "image_url"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Wireless Noise-Cancelling Headphones", "class": "input-field"}),
            "image": forms.FileInput(attrs={"class": "file-input block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"}),
            "image_url": forms.URLInput(attrs={"placeholder": "https://images.unsplash.com/... (optional photo link)", "class": "input-field"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Build grouped optgroups for cleaner category selection
        choices = [("", "-- Select Category or Subcategory --")]
        root_cats = Category.objects.filter(parent__isnull=True).prefetch_related("subcategories").order_by("order", "name")
        
        for root in root_cats:
            sub_choices = [(root.id, f"{root.name} (All / General)")]
            for sub in root.subcategories.all():
                sub_choices.append((sub.id, sub.name))
            choices.append((root.name, sub_choices))

        self.fields["category"].choices = choices

    def clean_price(self):
        raw_price = self.cleaned_data.get("price")
        if not raw_price:
            raise forms.ValidationError("Please enter a valid price.")
        # Handle comma as decimal separator
        cleaned_str = str(raw_price).strip().replace("$", "").replace(" ", "").replace(",", ".")
        try:
            val = Decimal(cleaned_str)
        except InvalidOperation:
            raise forms.ValidationError("Please enter a valid numeric price (e.g. 29.99).")

        if val <= Decimal("0.00"):
            raise forms.ValidationError("Price must be greater than zero.")
        return val

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is None or stock == "":
            return 1
        return max(0, int(stock))

    def clean_description(self):
        desc = self.cleaned_data.get("description", "").strip()
        if not desc:
            title = self.cleaned_data.get("title", "Product")
            return f"High quality {title}. Contact seller for more specifications."
        return desc

    def clean_image_url(self):
        url = self.cleaned_data.get("image_url", "").strip()
        if url and not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url
