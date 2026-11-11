from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path("order/<int:order_id>/success/", views.order_success_view, name="order_success"),
    path("my-orders/", views.my_orders_view, name="my_orders"),
]

