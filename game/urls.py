from django.urls import path
from .views import *

urlpatterns = [
    path("game/", game_view, name="game_view"),
    path("game-start", game_start, name="game_start"),
    path("start-result", start_result, name="start_result"),
    #path('game-over', game_over, "game_over"),
    path("game-settings-partial/", game_settings_partial, name="game_settings_partial"),
]