from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm,UserChangeForm

class CustomUserCreationForm(UserCreationForm):
    nation = forms.ChoiceField(
        choices=CustomUser.NATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    image = forms.ImageField(
        required=False,
        label="Upload Profile Image",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = CustomUser
        fields = ("username", "email", "nation", "image", "password1", "password2")
        
        
        

class UserUpdateForm(UserChangeForm):
    username = forms.CharField(
        required=False,  
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Username"
    )
    email = forms.EmailField(
        required=False,  
        widget=forms.EmailInput(attrs={"class": "form-control"}),
        label="Email"
    )
    nation = forms.ChoiceField(
        choices=CustomUser.NATION_CHOICES,
        required=False,  
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Nation"
    )
    image = forms.ImageField(
        required=False,  
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}), 
        label="Upload New Profile Image"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password', 'class': 'form-control'}),
        required=False,
        label="New Password"
    )
    password_repeat = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat New Password', 'class': 'form-control'}),
        required=False,
        label="Repeat New Password"
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "nation", "image"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        """Ensure password and password_repeat match if provided"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if password or password_repeat: 
            if password != password_repeat:
                self.add_error('password_repeat', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        """Update user fields and optionally set a new password"""
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('password')

        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()
        return user