from django.shortcuts import render
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout
from .form import CustomUserCreationForm, UserUpdateForm
from django.views.generic import (
    ListView,
    CreateView,
    FormView,
    RedirectView,
    View,
    DetailView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse


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


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = "profile_update.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    success_url = reverse_lazy("home_view")

    def get_object(self):
        return self.request.user


class LeaderboardListView(ListView):
    model = CustomUser
    template_name = "leaderboard.html"
    context_object_name = "users"
    queryset = CustomUser.objects.all().order_by("-stars")


# Views for partials (fetched and swapped into <main> in basic.html
# to not reload the entire page)


def leaderboard_swap(request):
    users = CustomUser.objects.all().order_by("-stars")
    return render(
        request,
        template_name="leaderboard_swap.html",
        context={"users": users},
    )

def login_swap(request):
    if request.method == "GET":
        # Just render the partial with an empty form
        form = AuthenticationForm()
        return render(request, 'login_swap.html', {'form': form})

    elif request.method == "POST":
        # Attempt to authenticate & login
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Instruct the browser to do a full redirect:
            response = HttpResponse(status=200)
            response['HX-Redirect'] = reverse('user_details', args=[user.username])
            return response
        # If form is not valid, re-render partial with errors:
        return render(request, 'login_swap.html', {'form': form})


def userdetail_swap(request):
    user = request.user
    return render(request, 'profile_swap.html', {'user': user})

@login_required
def userupdate_swap(request):
    user = request.user  # Hole den aktuellen Benutzer
    
    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect(reverse("home_view"))  # Nach erfolgreichem Update zur Startseite
    else:
        form = UserUpdateForm(instance=user)  # Lade das Formular mit bestehenden Werten

    return render(request, "profile_update_swap.html", {"form": form})

