from django.urls import path
from .views import *

urlpatterns = [
    path("game/", game_view, name="game_view"),
    path("game-start", game_start, name="game_start"),
    path("start-result", start_result, name="start_result"),
    path("game-flow", game_flow, name="game_flow"),
    path("after-submit", after_submit_view, name="after_submit"),

]