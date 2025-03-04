from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.core.cache import cache
from django.urls import reverse
import uuid

def home_view(request):
    return render(request, "homepage.html")


