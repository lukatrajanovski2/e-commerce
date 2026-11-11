from products.models import Category
from django.db.models import Count, Q

def categories_context(request):
    try:
        # Get root categories and prefetch their subcategories
        root_categories = Category.objects.filter(parent__isnull=True).prefetch_related(
            "subcategories"
        ).order_by("order", "name")
        return {
            "root_categories": root_categories,
        }
    except Exception:
        return {
            "root_categories": [],
        }

