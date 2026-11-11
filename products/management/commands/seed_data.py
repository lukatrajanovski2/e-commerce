from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from accounts.models import SellerProfile
from products.models import Category, Product
from decimal import Decimal

CATEGORIES_DATA = [
    {
        "name": "Electronics & Tech",
        "icon": "cpu",
        "order": 1,
        "subcategories": [
            "Smartphones & Tablets",
            "Laptops & Computers",
            "Audio & Headphones",
            "Smart Watches & Wearables",
            "Cameras & Drones",
            "Gaming Consoles & Accessories",
        ],
    },
    {
        "name": "Fashion & Apparel",
        "icon": "shirt",
        "order": 2,
        "subcategories": [
            "Men's Apparel",
            "Women's Apparel",
            "Footwear & Sneakers",
            "Jewelry & Watches",
            "Bags & Backpacks",
        ],
    },
    {
        "name": "Home & Kitchen",
        "icon": "home",
        "order": 3,
        "subcategories": [
            "Modern Furniture",
            "Kitchen Appliances & Cookware",
            "Bedding & Bath",
            "Home Decor & Wall Art",
            "Lighting & Lamps",
        ],
    },
    {
        "name": "Beauty & Wellness",
        "icon": "sparkles",
        "order": 4,
        "subcategories": [
            "Skincare & Serums",
            "Haircare & Styling",
            "Fragrances & Perfumes",
            "Makeup & Cosmetics",
        ],
    },
    {
        "name": "Sports & Outdoors",
        "icon": "activity",
        "order": 5,
        "subcategories": [
            "Fitness & Gym Gear",
            "Camping & Hiking",
            "Cycling & Bikes",
            "Team Sports Equipment",
        ],
    },
    {
        "name": "Books & Hobbies",
        "icon": "book-open",
        "order": 6,
        "subcategories": [
            "Best-selling Books",
            "Board Games & Puzzles",
            "Collectibles & Action Figures",
            "Musical Instruments",
        ],
    },
    {
        "name": "Automotive & Tools",
        "icon": "wrench",
        "order": 7,
        "subcategories": [
            "Car Electronics & Accessories",
            "Hand & Power Tools",
        ],
    },
]

SAMPLE_PRODUCTS = [
    {
        "title": "Ultra-Slim 15\" Pro Laptop M3",
        "category": "Laptops & Computers",
        "price": Decimal("1299.99"),
        "stock": 14,
        "description": "Blazing fast 12-core performance with 18-hour battery life, 16GB unified memory, and 512GB SSD storage in a lightweight aluminum unibody.",
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Acoustic Noise-Cancelling Wireless Headphones",
        "category": "Audio & Headphones",
        "price": Decimal("249.50"),
        "stock": 25,
        "description": "Premium active noise cancellation with 35 hours playback, spatial audio support, and ultra-soft memory foam earcups.",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Flagship 5G Smartphone 256GB - Titanium Gray",
        "category": "Smartphones & Tablets",
        "price": Decimal("899.00"),
        "stock": 18,
        "description": "Dynamic 120Hz OLED display, triple pro-grade camera sensor system with 5x optical zoom, and fast wireless charging.",
        "image_url": "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Minimalist Smart Fitness Watch with GPS",
        "category": "Smart Watches & Wearables",
        "price": Decimal("189.99"),
        "stock": 30,
        "description": "Track heart rate, SpO2, sleep stages, and over 100 sports workouts with 10-day battery life and 50m water resistance.",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Classic Italian Leather Minimalist Sneakers",
        "category": "Footwear & Sneakers",
        "price": Decimal("135.00"),
        "stock": 20,
        "description": "Handcrafted full-grain Italian leather sneakers with cushioned insoles and durable vulcanized rubber outsoles.",
        "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Waterproof Commuter Roll-Top Backpack 25L",
        "category": "Bags & Backpacks",
        "price": Decimal("79.95"),
        "stock": 42,
        "description": "Weatherproof recycled nylon fabric, padded 16-inch laptop compartment, hidden security pocket, and ergonomic shoulder straps.",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Ergonomic Mesh Office Chair with Lumbar Support",
        "category": "Modern Furniture",
        "price": Decimal("289.00"),
        "stock": 12,
        "description": "Breathable high-density mesh, 3D adjustable armrests, pneumatic height adjustment, and smooth-rolling PU caster wheels.",
        "image_url": "https://images.unsplash.com/photo-1580481077195-c22ae2b1e42f?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Precision Espresso Machine & Milk Frother",
        "category": "Kitchen Appliances & Cookware",
        "price": Decimal("449.99"),
        "stock": 8,
        "description": "15-bar Italian pump for optimal crema extraction, commercial style steam wand for silky microfoam latte art.",
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Handcrafted Ceramic Table Lamp with Linen Shade",
        "category": "Lighting & Lamps",
        "price": Decimal("64.50"),
        "stock": 19,
        "description": "Warm ambient lighting crafted from stoneware ceramic with a textured off-white linen drum shade. Fits E26 bulbs.",
        "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Hydrating Hyaluronic Acid & Vitamin C Serum",
        "category": "Skincare & Serums",
        "price": Decimal("38.00"),
        "stock": 55,
        "description": "Dermatologist-tested daily brightening and anti-aging serum with pure botanical hyaluronic acid and stabilized Vitamin C.",
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Adjustable Quick-Select Dumbbell Pair (5-52.5 lbs)",
        "category": "Fitness & Gym Gear",
        "price": Decimal("329.00"),
        "stock": 10,
        "description": "Turn the dial to instantly change resistance from 5 lbs up to 52.5 lbs per dumbbell. Space-saving workout system.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Ultralight 2-Person Backpacking Tent",
        "category": "Camping & Hiking",
        "price": Decimal("195.00"),
        "stock": 16,
        "description": "Under 3.8 lbs total trail weight, waterproof silicone-coated ripstop rainfly, and DAC featherlight aluminum poles.",
        "image_url": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Strategy Board Game - Collectors Edition",
        "category": "Board Games & Puzzles",
        "price": Decimal("59.99"),
        "stock": 22,
        "description": "Award-winning tile placement civilization game with custom wooden meeples, double-sided board, and mini expansions.",
        "image_url": "https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "20V Brushless Cordless Drill & Impact Driver Kit",
        "category": "Hand & Power Tools",
        "price": Decimal("169.00"),
        "stock": 15,
        "description": "Compact high-torque brushless motors, two 2.0Ah lithium-ion batteries, 30-minute rapid charger, and heavy-duty tool bag.",
        "image_url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Premium Wireless Gaming Controller",
        "category": "Gaming Consoles & Accessories",
        "price": Decimal("69.99"),
        "stock": 35,
        "description": "Hall-effect magnetic thumbsticks with zero stick drift, textured rubber grips, programmable rear paddle buttons, and low-latency Bluetooth.",
        "image_url": "https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?w=800&auto=format&fit=crop&q=80",
    },
    {
        "title": "Organic Heavyweight Cotton Oversized Tee",
        "category": "Men's Apparel",
        "price": Decimal("42.00"),
        "stock": 60,
        "description": "280 GSM premium organic combed cotton, relaxed drop-shoulder cut, pre-shrunk for an enduring shape.",
        "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80",
    },
]

class Command(BaseCommand):
    help = "Seed database with 30+ categories/subcategories, demo sellers, and sample products."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding categories and subcategories..."))

        cat_lookup = {}
        total_created = 0

        for cat_info in CATEGORIES_DATA:
            root_slug = slugify(cat_info["name"])
            root_cat, created = Category.objects.get_or_create(
                slug=root_slug,
                defaults={
                    "name": cat_info["name"],
                    "icon": cat_info.get("icon", "tag"),
                    "order": cat_info.get("order", 0),
                    "parent": None,
                },
            )
            cat_lookup[root_cat.name] = root_cat
            if created:
                total_created += 1

            for sub_name in cat_info["subcategories"]:
                sub_slug = slugify(sub_name)
                sub_cat, sub_created = Category.objects.get_or_create(
                    slug=sub_slug,
                    defaults={
                        "name": sub_name,
                        "parent": root_cat,
                        "icon": "circle",
                        "order": 10,
                    },
                )
                cat_lookup[sub_name] = sub_cat
                if sub_created:
                    total_created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded categories! Total in DB: {Category.objects.count()} (Root: {Category.objects.filter(parent__isnull=True).count()}, Subcategories: {Category.objects.filter(parent__isnull=False).count()})"))

        # Create demo users and sellers
        self.stdout.write(self.style.NOTICE("Creating demo accounts and sellers..."))

        seller_user1, _ = User.objects.get_or_create(
            username="apex_electronics",
            defaults={"email": "apex@ecommerce.local", "first_name": "Apex", "last_name": "Store"},
        )
        seller_user1.set_password("password123")
        seller_user1.save()

        seller_prof1, _ = SellerProfile.objects.get_or_create(
            user=seller_user1,
            defaults={
                "store_name": "Apex Electronics & Gadgets",
                "bio": "Authorized retailer for premier tech, audio gear, and gaming hardware.",
                "phone_number": "+1 (555) 234-5678",
            },
        )

        seller_user2, _ = User.objects.get_or_create(
            username="nordic_living",
            defaults={"email": "nordic@ecommerce.local", "first_name": "Nordic", "last_name": "Studio"},
        )
        seller_user2.set_password("password123")
        seller_user2.save()

        seller_prof2, _ = SellerProfile.objects.get_or_create(
            user=seller_user2,
            defaults={
                "store_name": "Nordic Living & Fashion",
                "bio": "Curated minimalist home aesthetics, apparel, and lifestyle accessories.",
                "phone_number": "+1 (555) 876-5432",
            },
        )

        buyer_user, _ = User.objects.get_or_create(
            username="buyer1",
            defaults={"email": "buyer@ecommerce.local", "first_name": "John", "last_name": "Shopper"},
        )
        buyer_user.set_password("password123")
        buyer_user.save()

        # Seed products
        self.stdout.write(self.style.NOTICE("Creating sample products..."))
        products_created = 0

        for i, item in enumerate(SAMPLE_PRODUCTS):
            cat_obj = cat_lookup.get(item["category"])
            if not cat_obj:
                continue

            seller = seller_prof1 if i % 2 == 0 else seller_prof2
            slug = slugify(item["title"])

            prod, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "seller": seller,
                    "category": cat_obj,
                    "title": item["title"],
                    "description": item["description"],
                    "price": item["price"],
                    "stock": item["stock"],
                    "image_url": item["image_url"],
                    "is_active": True,
                },
            )
            if created:
                products_created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded! Total products in DB: {Product.objects.count()} (New created: {products_created})"))
        self.stdout.write(self.style.SUCCESS("Demo credentials: Username: 'buyer1' or 'apex_electronics', Password: 'password123'"))

