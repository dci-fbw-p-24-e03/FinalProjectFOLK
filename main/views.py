from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.core.cache import cache
from django.urls import reverse
import uuid

from django.core.mail import send_mail
from .form import ContactForm
from django.conf import settings

def home_view(request):
    return render(request, "homepage.html")

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

           #no real email!!! 
            print(f"formular send!: {name} ({email}) said: {message}")

            return redirect('contact_success')
    else:
        form = ContactForm()

    return render(request, 'contact_us.html', {'form': form})

def contact_success(request):
    return render(request, 'contact_us_success.html')


