from django.urls import path
from .views import *


urlpatterns = [
     path("users/<slug:username>/",UserDetailView.as_view(),name="user_details"),
     path("login/", UserLoginView.as_view(), name="login_view"),
     path("logout/",UserLogoutView.as_view(),name="logout_view"),
     path("register/", UserRegisterView.as_view(), name="register_view"),
     path("users/<slug:username>/update/",UserUpdateView.as_view(),name="user_update"),
     path('leaderboard/', LeaderboardListView.as_view(), name='leaderboard'),
     path('leaderboard-partial/', leaderboard_partial, name='leaderboard_partial'),
     path('login-partial/', login_partial, name='login_partial'),
     path('users-partial/', userdetail_partial, name='profile_partial'),
 ]
