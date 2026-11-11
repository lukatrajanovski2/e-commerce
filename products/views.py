from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from accounts.models import SellerProfile
from .models import Category, Product
from .forms import ProductForm

def home_view(request):
    """
    Main storefront view:
    - Left sidebar: Hierarchical category & subcategory browser with product counts.
    - Main feed: Newest products (ordered by -created_at).
    - Supports category filtering, search queries, and store filtering.
    """
    selected_slug = request.GET.get("category", "").strip()
    search_query = request.GET.get("q", "").strip()
    sort_by = request.GET.get("sort", "newest")
    store_id = request.GET.get("store", "").strip()

    products = Product.objects.filter(is_active=True).select_related("seller", "category", "category__parent")

    filtered_store = None
    if store_id:
        filtered_store = get_object_or_404(SellerProfile, id=store_id)
        products = products.filter(seller=filtered_store)

    selected_category = None
    if selected_slug:
        selected_category = get_object_or_404(Category, slug=selected_slug)
        # Match products in this category or any of its subcategories
        cat_ids = selected_category.get_descendants_ids()
        products = products.filter(category_id__in=cat_ids)

    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(seller__store_name__icontains=search_query)
        )

    # Sorting
    if sort_by == "price_asc":
        products = products.order_by("price")
    elif sort_by == "price_desc":
        products = products.order_by("-price")
    elif sort_by == "oldest":
        products = products.order_by("created_at")
    else:
        # Default: newest items
        products = products.order_by("-created_at")

    # Pagination: 12 products per page
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Calculate category counts dynamically
    categories_tree = []
    root_cats = Category.objects.filter(parent__isnull=True).prefetch_related("subcategories").order_by("order", "name")
    
    for root in root_cats:
        all_desc_ids = root.get_descendants_ids()
        root_count = Product.objects.filter(is_active=True, category_id__in=all_desc_ids).count()
        
        subs_with_counts = []
        for sub in root.subcategories.all():
            sub_count = Product.objects.filter(is_active=True, category=sub).count()
            subs_with_counts.append({
                "category": sub,
                "count": sub_count,
                "is_active": selected_category and selected_category.id == sub.id,
            })
        
        categories_tree.append({
            "category": root,
            "total_count": root_count,
            "subcategories": subs_with_counts,
            "is_active": selected_category and selected_category.id == root.id,
            "has_active_child": selected_category and selected_category.id in [s["category"].id for s in subs_with_counts],
        })

    return render(
        request,
        "products/home.html",
        {
            "page_obj": page_obj,
            "products": page_obj.object_list,
            "categories_tree": categories_tree,
            "selected_category": selected_category,
            "search_query": search_query,
            "sort_by": sort_by,
            "filtered_store": filtered_store,
            "total_products_count": paginator.count,
        },
    )


def product_detail_view(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("seller", "category", "category__parent"),
        slug=slug,
        is_active=True,
    )
    
    # Check if the current logged-in user is the seller of this item
    is_owner = (
        request.user.is_authenticated 
        and hasattr(request.user, "seller_profile") 
        and product.seller.user_id == request.user.id
    )

    # Related products from same category or parent category
    related_ids = product.category.get_descendants_ids() if product.category.is_root else [product.category.id]
    if product.category.parent:
        related_ids = product.category.parent.get_descendants_ids()

    related_products = (
        Product.objects.filter(is_active=True, category_id__in=related_ids)
        .exclude(id=product.id)
        .order_by("-created_at")[:4]
    )

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
            "is_owner": is_owner,
        },
    )


@login_required
def product_create_view(request):
    """Only authenticated users who have registered as a seller can list items."""
    if not request.user.is_seller:
        messages.warning(request, "You must register as a seller before listing items for sale.")
        return redirect("become_seller")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.seller_profile
            product.save()
            messages.success(request, f"🎉 Product '{product.title}' was added successfully to your store inventory!")
            return redirect("seller_dashboard")
        else:
            messages.error(request, "Could not add product. Please check the highlighted errors below.")
    else:
        form = ProductForm()

    return render(request, "products/product_form.html", {"form": form, "action": "List New Item"})


@login_required
def seller_dashboard_view(request):
    if not request.user.is_seller:
        messages.info(request, "Register as a seller to access the seller dashboard.")
        return redirect("become_seller")

    seller = request.user.seller_profile
    products = Product.objects.filter(seller=seller).select_related("category").order_by("-created_at")

    total_stock = sum(p.stock for p in products)
    active_count = products.filter(is_active=True).count()

    return render(
        request,
        "products/seller_dashboard.html",
        {
            "seller": seller,
            "products": products,
            "total_stock": total_stock,
            "active_count": active_count,
        },
    )


@login_required
def product_edit_view(request, slug):
    if not request.user.is_seller:
        return redirect("become_seller")

    product = get_object_or_404(Product, slug=slug, seller=request.user.seller_profile)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.title}' updated successfully.")
            return redirect("seller_dashboard")
        else:
            messages.error(request, "Could not update product. Please check the errors below.")
    else:
        form = ProductForm(instance=product)

    return render(request, "products/product_form.html", {"form": form, "action": "Edit Item", "product": product})


@login_required
def product_delete_view(request, slug):
    if not request.user.is_seller:
        return redirect("become_seller")

    product = get_object_or_404(Product, slug=slug, seller=request.user.seller_profile)

    if request.method == "POST":
        title = product.title
        product.delete()
        messages.success(request, f"Product '{title}' was removed.")
        return redirect("seller_dashboard")

    return render(request, "products/product_confirm_delete.html", {"product": product})
