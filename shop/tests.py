import os
from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.auth import get_user_model
from shop.models import Product, Order


# tests for models.py
# Product: creation, default values, __str__ method, many-to-many relation Product/User
# Order: creation, __str__ method
User = get_user_model()


class ProductModelTest(TestCase):
    def setUp(self):
        """Create a test product"""
        # Ensure no previous test image remains
        image_path = os.path.join(settings.MEDIA_ROOT, "product_images/test_image.jpeg")
        if os.path.exists(image_path):
            os.remove(image_path)

        image = SimpleUploadedFile(
            "test_image.jpeg", b"\x00" * 1024, content_type="image/jpeg"
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="This is a test product.",
            price=Decimal("9.99"),
            image=image,
            category="joker",
        )

    def test_product_creation(self):
        """Test if the product is created correctly"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.description, "This is a test product.")
        self.assertEqual(self.product.price, Decimal("9.99"))
        self.assertEqual(self.product.category, "joker")
        self.assertEqual(self.product.image, "product_images/test_image.jpeg")

    def test_default_category(self):
        """Test if the default category is set to 'skins'"""
        image_path = os.path.join(settings.MEDIA_ROOT, "product_images/test_image.jpeg")
        if os.path.exists(image_path):
            os.remove(image_path)
        default_product = Product.objects.create(
            name="Default Product",
            description="This is a default category test.",
            price=Decimal("5.00"),
            image=SimpleUploadedFile(
                "test_image.jpeg", b"\x00" * 1024, content_type="image/jpeg"
            ),
        )
        self.assertEqual(default_product.category, "skins")

    def test_product_string_representation(self):
        """Test the __str__ method of Product"""
        self.assertEqual(str(self.product), "Test Product (joker)")

    def test_product_user_relationship(self):
        """Test many-to-many relationship between Product and Users"""
        user = User.objects.create_user(username="testuser", password="password123")
        self.product.users.add(user)
        self.assertIn(user, self.product.users.all())

    def test_product_creation_without_image(self):
        """Test if a product can be created without an image"""
        product = Product(
            name="No Image Product",
            description="This product has no image.",
            price=Decimal("5.99"),
            category="skins",
            # image is missing
        )
        # Now call full_clean() inside the assertion to check for ValidationError
        with self.assertRaises(ValidationError) as context:
            product.full_clean()

        # Optional: Check that the error is specifically about the image field
        self.assertIn("image", context.exception.message_dict)

    def test_product_fails_without_image(self):
        """Test if product creation fails when required fields are missing"""
        product = Product(
            # name is missing
            description="This should fail.",
            price=Decimal("5.99"),
            category="skins",
            image=None,  # image is missing
        )
        with self.assertRaises(ValidationError):
            product.full_clean()


class OrderModelTest(TestCase):
    def setUp(self):
        """Create a test user and product before each test"""
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        image_path = os.path.join(settings.MEDIA_ROOT, "product_images/test_image.jpeg")
        if os.path.exists(image_path):
            os.remove(image_path)

        image = SimpleUploadedFile(
            "test_image.jpeg", b"\x00" * 1024, content_type="image/jpeg"
        )
        self.product = Product.objects.create(
            name="Order Product",
            description="This is an order test.",
            price=Decimal("15.99"),
            image=image,
            category="skins",
        )
        self.order = Order.objects.create(
            user=self.user, product=self.product, quantity=2, total=Decimal("31.98")
        )

    def test_order_creation(self):
        """Test if an order is created correctly"""
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.product, self.product)
        self.assertEqual(self.order.quantity, 2)
        self.assertEqual(self.order.total, Decimal("31.98"))
        self.assertIsNotNone(self.order.order_date)

    def test_order_string_representation(self):
        """Test the __str__ method of Order"""
        self.assertEqual(
            str(self.order),
            f"Order by {self.user.username} for {self.product.name} (x2)",
        )


# tests vor views.py
# ShopView: load page, login required, purchase success, insufficient funds
# ShopSwapView: same tests as for ShopView

User = get_user_model()


class ShopViewTests(TestCase):
    def setUp(self):
        """Create test products and a user"""
        self.user = User.objects.create_user(
            username="testuser", password="password123", coins=20
        )
        image_path = os.path.join(settings.MEDIA_ROOT, "product_images/test_image.jpeg")
        if os.path.exists(image_path):
            os.remove(image_path)

        image = SimpleUploadedFile(
            "test_image.jpeg", b"\x00" * 1024, content_type="image/jpeg"
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="Shop product for test.",
            price=Decimal("10.00"),
            image=image,
            category="joker",
        )

    def test_shop_page_loads(self):
        """Test if the shop page loads correctly"""
        response = self.client.get(reverse("shop_view"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop.html")
        self.assertContains(response, "Test Product")

    def test_buy_product_page_requires_login(self):
        """Test if the buy product page redirects if not logged in"""
        response = self.client.get(reverse("buy_product", args=[self.product.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Log in and try again
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("buy_product", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "buy_confirmation.html")
        self.assertContains(response, "Test Product")

    def test_confirm_purchase_success(self):
        """Test if a user can successfully purchase a product"""
        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse("confirm_purchase", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "purchase_success.html")

        # Check if the order was created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.product, self.product)
        self.assertEqual(order.quantity, 1)
        self.assertEqual(order.total, Decimal("10.00"))

        # Check if coins were deducted
        self.user.refresh_from_db()
        self.assertEqual(self.user.coins, 10)  # 20 - 10 = 10

    def test_confirm_purchase_insufficient_funds(self):
        """Test if a user cannot buy a product without enough coins"""
        self.user.coins = 5  # Not enough to buy the product
        self.user.save()

        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse("confirm_purchase", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "purchase_success.html")
        self.assertContains(response, "Not enough coins to complete the purchase.")

        # No order should be created
        self.assertEqual(Order.objects.count(), 0)


class ShopSwapViewTests(TestCase):
    def setUp(self):
        """Create test products and a user"""
        self.user = User.objects.create_user(
            username="testuser", password="password123", coins=20
        )
        image_path = os.path.join(settings.MEDIA_ROOT, "product_images/test_image.jpeg")
        if os.path.exists(image_path):
            os.remove(image_path)

        image = SimpleUploadedFile(
            "test_image.jpeg", b"\x00" * 1024, content_type="image/jpeg"
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="Shop product for test.",
            price=Decimal("10.00"),
            image=image,
            category="joker",
        )

    def test_shop_swap_loads(self):
        """Test if the shop swap page loads correctly"""
        response = self.client.get(reverse("shop_swap"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop_swap.html")
        self.assertContains(response, "Test Product")

    def test_buy_product_swap_requires_login(self):
        """Test if the buy product swap page redirects if not logged in"""
        response = self.client.get(reverse("buy_product_swap", args=[self.product.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Log in and try again
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("buy_product_swap", args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "buy_confirmation_swap.html")
        self.assertContains(response, "Test Product")

    def test_confirm_purchase_swap_success(self):
        """Test successful purchase using shop_swap"""
        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            reverse("confirm_purchase_swap", args=[self.product.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "purchase_success_swap.html")

        self.assertEqual(Order.objects.count(), 1)
        self.user.refresh_from_db()
        self.assertEqual(self.user.coins, 10)

    def test_confirm_purchase_swap_insufficient_funds(self):
        """Test failed purchase due to insufficient funds"""
        self.user.coins = 5
        self.user.save()

        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            reverse("confirm_purchase_swap", args=[self.product.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "purchase_success_swap.html")
        self.assertContains(response, "Not enough coins to complete the purchase.")
        self.assertEqual(Order.objects.count(), 0)
