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
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password', 'class': 'form-control'}),
        required=False
    )
    password_repeat = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat New Password', 'class': 'form-control'}),
        required=False
    )
    nation = forms.ChoiceField(choices=CustomUser.NATION_CHOICES, required=False)
    image = forms.ImageField(
        required=False,
        label="Upload New Profile Image",
        widget=forms.FileInput(attrs={'class': 'form-control'}) 
    )
    
    class Meta:
        model = CustomUser
        fields = ["username", "email", "nation", "image"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')
        
        if password or password_repeat:
            if password != password_repeat:
                raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user