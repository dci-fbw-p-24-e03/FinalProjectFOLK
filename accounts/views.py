from django.shortcuts import render
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from .form import CustomUserCreationForm,UserUpdateForm
from django.views.generic import ListView, CreateView, FormView, RedirectView, View,DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

class UserLoginView(FormView):
    form_class = AuthenticationForm
    template_name = "login.html"
    success_url = reverse_lazy("home_view")

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        print(self.request)
        return super().form_valid(form)


class UserLogoutView(RedirectView):
    url = reverse_lazy("home_view")

    def get(self, request, *args, **kwargs):
        logout(request)
        print(self.request.user)
        return super().get(request, *args, **kwargs)


class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "register.html"
    success_url = reverse_lazy("home_view")

class UserDetailView(DetailView):
    model = CustomUser
    template_name = "profile.html"
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

class UserUpdateView(LoginRequiredMixin,UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = "profile_update.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    success_url = reverse_lazy("home_view")

    def get_object(self):
        return self.request.user
