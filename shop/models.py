from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("joker", "Joker"),
        ("skins", "Skins"),
        ("opponents", "Opponents"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="product_images/")
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="skins"
    )
    users = models.ManyToManyField(
        "accounts.CustomUser", blank=True)  # Many-to-many relationship

    def clean(self):
        """Ensure that all required fields are filled"""
        if not self.name:
            raise ValidationError({"name": "This field is required."})
        if not self.description:
            raise ValidationError({"description": "This field is required."})
        if not self.price:
            raise ValidationError({"price": "This field is required."})
        if not self.category:
            raise ValidationError({"category": "This field is required."})
        if not self.image:
            raise ValidationError({"image": "An image is required."})

    def save(self, *args, **kwargs):
        """Run validation before saving"""
        self.full_clean()  # 'clean()' is apllied before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category})"


class Order(models.Model):
    user = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.CASCADE
    )  # link to User
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # link to product
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)  # total price
    order_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (
            f"Order by {self.user.username} for {self.product.name} (x{self.quantity})"
        )
