from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("product/<slug:slug>/", views.product_detail_view, name="product_detail"),
    path("sell/", views.product_create_view, name="product_create"),
    path("seller/dashboard/", views.seller_dashboard_view, name="seller_dashboard"),
    path("seller/product/<slug:slug>/edit/", views.product_edit_view, name="product_edit"),
    path("seller/product/<slug:slug>/delete/", views.product_delete_view, name="product_delete"),
]

