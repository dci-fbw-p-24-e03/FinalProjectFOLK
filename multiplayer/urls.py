from django.urls import path
from .views import (
    results,
    multi_play,
    join_matchmaking,
    waiting_room,
    check_match,
    leave_matchmaking,
    game_room,
)

urlpatterns = [
    path("join-matchmaking/", join_matchmaking, name="join_matchmaking"),
    path("waiting-room/<str:user_id>/", waiting_room, name="waiting_room"),
    path("check-match/<str:user_id>/", check_match, name="check_match"),
    path("leave-matchmaking/", leave_matchmaking, name="leave_matchmaking"),
    path("game-room/<str:room_id>/", game_room, name="game_room"),
    path("multi_play/", multi_play, name="multi_play"),
    path("results/", results, name="results"),
]
