from django.test import TestCase
from django.core.files.base import ContentFile
from .models import CustomUser
from io import BytesIO
from PIL import Image
import os

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .form import CustomUserCreationForm, UserUpdateForm

# test for models.py
# CustomUser: Creation, default values, image resizing, __str__ method
# Authentication: Can users log in and log out correctly?
# User registration: Does the registration form work? Is the user saved?

class CustomUserModelTest(TestCase):
    def setUp(self):
        """Set up a test user before each test"""
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="securepass",
            stars=10,
            coins=5,
            nation="DE"
        )

    def test_user_creation(self):
        """Test if a user is created correctly"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.stars, 10)
        self.assertEqual(self.user.coins, 5)
        self.assertEqual(self.user.nation, "DE")

    def test_default_values(self):
        """Test if default values are correctly set"""
        new_user = CustomUser.objects.create_user(username="newuser", email="new@example.com", password="securepass")
        self.assertEqual(new_user.coins, 0)
        self.assertEqual(new_user.nation, "DE")
        self.assertEqual(new_user.stars, 0)

    def test_image_resizing(self):
        """Test if the image resizing method works correctly"""
        
        # Generate a real in-memory image (1000x1000 px)
        image = Image.new("RGB", (1000, 1000), color=(255, 0, 0))  # Red image
        img_io = BytesIO()
        image.save(img_io, format="JPEG")  # Save as real JPEG
        img_content = ContentFile(img_io.getvalue(), "test_image.jpg")

        # Assign to user image field
        self.user.image = img_content
        self.user.save()

        # Re-open the saved image to check resizing
        img = Image.open(self.user.image.path)
        self.assertLessEqual(img.height, 300)
        self.assertLessEqual(img.width, 300)

        # close img before deleting (important for Windows, nice to have for Linux/macOS)
        img.close()

        # Clean up
        if os.path.exists(self.user.image.path):
            os.remove(self.user.image.path)

    def test_string_representation(self):
        """Test the string representation of the user model"""
        self.assertEqual(str(self.user), "testuser")


# test for views.py
# Profile Views: Can a user view and update their profile?
# Leaderboard: Are users displayed in the correct order?

User = get_user_model()

class UserAuthenticationTests(TestCase):
    def setUp(self):
        """Create a test user"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="securepass")

    def test_login_view(self):
        """Test login page loads and processes login correctly"""
        response = self.client.get(reverse("login_swap"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], AuthenticationForm)

        # Attempt login
        response = self.client.post(reverse("login_swap"), {"username": "testuser", "password": "securepass"})
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """Test logout redirects correctly"""
        self.client.login(username="testuser", password="securepass")
        response = self.client.get(reverse("logout_view"))
        self.assertEqual(response.status_code, 302)  # Redirect

class UserRegisterViewTest(TestCase):
    def test_register_view_get(self):
        """Test if registration page loads correctly"""
        response = self.client.get(reverse("register_swap"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)

    def test_register_view_post(self):
        """Test user registration"""
        response = self.client.post(reverse("register_swap"), {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!"
        })
        self.assertEqual(response.status_code, 302)  # Redirect to home_view

class UserProfileTests(TestCase):
    def setUp(self):
        """Create a test user"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="securepass")
        self.client.login(username="testuser", password="securepass")

    def test_user_profile_view(self):
        """Test if the profile page loads for the logged-in user"""
        response = self.client.get(reverse("profile_swap"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")  # Ensure username is displayed

    def test_user_update_view_get(self):
        """Test if profile update page loads correctly"""
        response = self.client.get(reverse("userupdate_swap"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], UserUpdateForm)

    def test_user_update_view_post(self):
        """Test updating user profile"""
        response = self.client.post(reverse("userupdate_swap"), {
            "username": "updateduser",
            "email": "updated@example.com"
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update

        # Check if user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.email, "updated@example.com")

class LeaderboardViewTest(TestCase):
    def setUp(self):
        """Create multiple test users"""
        self.user1 = User.objects.create_user(username="user1", stars=50)
        self.user2 = User.objects.create_user(username="user2", stars=100)
        self.user3 = User.objects.create_user(username="user3", stars=75)

    def test_leaderboard_view(self):
        """Test if leaderboard loads with sorted users"""
        response = self.client.get(reverse("leaderboard_swap"))
        self.assertEqual(response.status_code, 200)
        users = list(response.context["users"])
        self.assertEqual(users[0].username, "user2")  # Highest stars
        self.assertEqual(users[1].username, "user3")
        self.assertEqual(users[2].username, "user1")


# tests for form.py
# validation logic: password confirmation, required fields
# are widgets rendered correctly?
# are errors handled correctly?

class CustomUserCreationFormTest(TestCase):
    def test_valid_data(self):
        """Test if the registration form is valid with correct data"""
        form = CustomUserCreationForm(data={
            "username": "testuser",
            "email": "test@example.com",
            "nation": "DE",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!"
        })
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """Test if the form correctly detects mismatched passwords"""
        form = CustomUserCreationForm(data={
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass123!",
            "password2": "WrongPass321!"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_missing_required_fields(self):
        """Test if the form fails when required fields are missing"""
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password1", form.errors)
        self.assertIn("password2", form.errors)

class UserUpdateFormTest(TestCase):
    def setUp(self):
        """Create a test user for update tests"""
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="SecurePass123!")

    def test_valid_update(self):
        """Test if updating user profile works"""
        form = UserUpdateForm(instance=self.user, data={
            "username": "updateduser",
            "email": "updated@example.com",
            "nation": "FR"
        })
        self.assertTrue(form.is_valid())

    def test_password_update(self):
        """Test password update functionality"""
        form = UserUpdateForm(instance=self.user, data={
            "password": "NewPass123!",
            "password_repeat": "NewPass123!"
        })
        print("Form Errors:", form.errors)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """Test if password mismatch is correctly detected"""
        form = UserUpdateForm(instance=self.user, data={
            "password": "NewPass123!",
            "password_repeat": "WrongPass321!"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password_repeat", form.errors)
