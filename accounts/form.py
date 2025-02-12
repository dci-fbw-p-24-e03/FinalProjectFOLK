from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm,UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username","email","password1","password2")

class UserUpdateForm(UserChangeForm):
    
    
    class Meta:
        model = CustomUser
        fields = ["username","email"]