from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from accounts.models import SellerProfile
from products.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order

class EcommercePlatformTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Create Categories and Subcategories
        self.parent_cat = Category.objects.create(name="Electronics", slug="electronics", order=1)
        self.sub_cat1 = Category.objects.create(name="Laptops", slug="laptops", parent=self.parent_cat, order=1)
        self.sub_cat2 = Category.objects.create(name="Phones", slug="phones", parent=self.parent_cat, order=2)

        # 2. Create Regular User
        self.buyer = User.objects.create_user(username="regular_buyer", password="password123", email="buyer@test.com")

        # 3. Create Seller User
        self.seller_user = User.objects.create_user(username="tech_seller", password="password123", email="seller@test.com")
        self.seller_profile = SellerProfile.objects.create(
            user=self.seller_user,
            store_name="Tech Hub",
            phone_number="1234567890",
            bio="Electronics store"
        )

        # 4. Create Sample Products
        self.product1 = Product.objects.create(
            seller=self.seller_profile,
            category=self.sub_cat1,
            title="Gaming Laptop 16GB",
            price=Decimal("999.00"),
            stock=5,
            description="High-performance gaming laptop"
        )
        self.product2 = Product.objects.create(
            seller=self.seller_profile,
            category=self.sub_cat2,
            title="Smart Phone 128GB",
            price=Decimal("499.00"),
            stock=10,
            description="5G Flagship phone"
        )

    def test_category_hierarchy_and_descendants(self):
        """Test that categories properly link parents, subcategories, and descendant IDs."""
        self.assertTrue(self.parent_cat.is_root)
        self.assertFalse(self.sub_cat1.is_root)
        self.assertEqual(self.sub_cat1.parent, self.parent_cat)
        
        descendant_ids = self.parent_cat.get_descendants_ids()
        self.assertIn(self.parent_cat.id, descendant_ids)
        self.assertIn(self.sub_cat1.id, descendant_ids)
        self.assertIn(self.sub_cat2.id, descendant_ids)

    def test_newest_products_on_homepage(self):
        """Test that homepage loads products ordered by -created_at."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gaming Laptop 16GB")
        self.assertContains(response, "Smart Phone 128GB")
        
        products = list(response.context["products"])
        # Most recently created item should appear first
        self.assertEqual(products[0], self.product2)
        self.assertEqual(products[1], self.product1)

    def test_category_filtering(self):
        """Test filtering products by parent category and subcategory."""
        # Filter by subcategory
        response = self.client.get(reverse("home"), {"category": "laptops"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gaming Laptop 16GB")
        self.assertNotContains(response, "Smart Phone 128GB")

        # Filter by parent category (should include both subcategories)
        response_parent = self.client.get(reverse("home"), {"category": "electronics"})
        self.assertEqual(response_parent.status_code, 200)
        self.assertContains(response_parent, "Gaming Laptop 16GB")
        self.assertContains(response_parent, "Smart Phone 128GB")

    def test_seller_guard_on_product_creation(self):
        """Only authenticated users who are sellers can access and submit the product create view."""
        # 1. Unauthenticated user -> redirects to login
        response = self.client.get(reverse("product_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

        # 2. Regular user (not a seller) -> redirects to become_seller
        self.client.login(username="regular_buyer", password="password123")
        response = self.client.get(reverse("product_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("become-seller", response.url)
        self.client.logout()

        # 3. Seller user -> gets 200 OK
        self.client.login(username="tech_seller", password="password123")
        response = self.client.get(reverse("product_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List New Item")

        # 4. Seller posts a new product
        post_data = {
            "title": "Mechanical Keyboard RGB",
            "category": self.sub_cat1.id,
            "price": "89.99",
            "stock": 15,
            "description": "Tactile blue switches",
            "image_url": "https://example.com/keyboard.jpg"
        }
        res = self.client.post(reverse("product_create"), data=post_data)
        self.assertEqual(res.status_code, 302)
        
        # Verify product created
        new_product = Product.objects.get(title="Mechanical Keyboard RGB")
        self.assertEqual(new_product.seller, self.seller_profile)
        self.assertEqual(new_product.price, Decimal("89.99"))

    def test_cart_and_delivery_options(self):
        """Test adding item to cart, selecting delivery option, and calculating total."""
        # Add product1 (price $999.00) to cart
        self.client.post(reverse("add_to_cart", args=[self.product1.id]), {"quantity": 1})
        
        # Check cart page
        cart_resp = self.client.get(reverse("cart_detail"))
        self.assertEqual(cart_resp.status_code, 200)
        cart = cart_resp.context["cart"]
        self.assertEqual(cart.item_count, 1)
        self.assertEqual(cart.subtotal, Decimal("999.00"))
        
        # Order is >= $50, so standard delivery is FREE ($0.00)
        self.assertEqual(cart.delivery_option, "standard")
        self.assertEqual(cart.delivery_fee, Decimal("0.00"))
        self.assertEqual(cart.grand_total, Decimal("999.00"))

        # Select Express delivery option
        self.client.post(reverse("cart_detail"), {"delivery_option": "express"})
        cart.refresh_from_db()
        self.assertEqual(cart.delivery_option, "express")
        self.assertEqual(cart.delivery_fee, Decimal("12.99"))
        self.assertEqual(cart.grand_total, Decimal("1011.99"))

        # Select Same-Day courier delivery option
        self.client.post(reverse("cart_detail"), {"delivery_option": "same_day"})
        cart.refresh_from_db()
        self.assertEqual(cart.delivery_option, "same_day")
        self.assertEqual(cart.delivery_fee, Decimal("19.99"))
        self.assertEqual(cart.grand_total, Decimal("1018.99"))

        # Select Store Pickup option
        self.client.post(reverse("cart_detail"), {"delivery_option": "pickup"})
        cart.refresh_from_db()
        self.assertEqual(cart.delivery_option, "pickup")
        self.assertEqual(cart.delivery_fee, Decimal("0.00"))
        self.assertEqual(cart.grand_total, Decimal("999.00"))

    def test_checkout_and_order_creation(self):
        """Test full checkout flow with delivery option and inventory decrement."""
        # Add product to cart
        self.client.post(reverse("add_to_cart", args=[self.product1.id]), {"quantity": 2})
        
        # Set Express delivery
        self.client.post(reverse("cart_detail"), {"delivery_option": "express"})

        # Submit checkout
        checkout_data = {
            "full_name": "Alice Wonderland",
            "email": "alice@example.com",
            "phone": "555-0199",
            "shipping_address": "456 Market St",
            "city": "Metropolis",
            "postal_code": "90210"
        }
        res = self.client.post(reverse("checkout"), data=checkout_data)
        self.assertEqual(res.status_code, 302)

        # Verify order exists
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.full_name, "Alice Wonderland")
        self.assertEqual(order.delivery_fee, Decimal("12.99"))
        self.assertEqual(order.subtotal, Decimal("1998.00"))
        self.assertEqual(order.grand_total, Decimal("2010.99"))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)

        # Verify inventory was decremented from 5 to 3
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, 3)
