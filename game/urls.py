from django.urls import path
from .views import *

urlpatterns = [
    path("game/", game_view, name="game_view"),
    path("game-update", game_update, name="game_update"),
    path("game-flow", game_flow, name="game_flow"),

]