from django.urls import path
from . import views

urlpatterns = [
    path("", views.cart_detail_view, name="cart_detail"),
    path("add/<int:product_id>/", views.add_to_cart_view, name="add_to_cart"),
    path("item/<int:item_id>/update/", views.update_cart_item_view, name="update_cart_item"),
    path("item/<int:item_id>/remove/", views.remove_cart_item_view, name="remove_cart_item"),
]

