from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Name'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': 'Your message:'})
    )


#settings.py:
#in case for real email!!! (contact us):

#from dotenv import load_dotenv
#load_dotenv()

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True

#EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER') 
#EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') 
#CONTACT_EMAIL = os.getenv('CONTACT_EMAIL')  
