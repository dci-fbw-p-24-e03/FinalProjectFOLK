from django.shortcuts import render
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.core.cache import cache
from django.urls import reverse
import uuid
from accounts.models import CustomUser  # Import User model

# Create your views here.
MATCHMAKING_POOL_KEY = "matchmaking_pool"





def join_matchmaking(request):
    user_id = str(request.user.id) if request.user.is_authenticated else str(uuid.uuid4())
    user_name = request.user.username if request.user.is_authenticated else f"Guest {user_id[:4]}"  # Use guest name if not authenticated

    waiting_players = cache.get(MATCHMAKING_POOL_KEY, [])

    # If the user is already in the pool, no need to add again, just send them to the waiting room
    if user_id in waiting_players:
        waiting_url = reverse("waiting_room", kwargs={"user_id": user_id})
        return JsonResponse({"status": "waiting", "user_id": user_id, "redirect": waiting_url})

    # If there are players in the pool, try to match them
    if waiting_players:
        opponent_id = waiting_players.pop(0)

        # Get the opponent's user data
        opponent = CustomUser.objects.get(id=opponent_id)  # Fetch opponent user
        opponent_data = {
            "id": opponent.id,
            "username": opponent.username,
            "image": opponent.image,
            "average": opponent.average_stars_per_game,
        }

        # Get the current user's data
        user = request.user
        user_data = {
            "id": user.id,
            "username": user.username,
            "image":user.image,
            "average": user.average_stars_per_game,
        }

        # Update the cache with the new state of the pool
        cache.set(MATCHMAKING_POOL_KEY, waiting_players, timeout=60)

        # Create a new game room for the matched players, including full user data
        room_id = str(uuid.uuid4())  # New unique game room id
        cache.set(f"game_room:{room_id}", {
            "players": [user_id, opponent_id],
            "player_data": [user_data, opponent_data]
        }, timeout=600)
        
        # *** NEW: Update active_game_rooms so that check_match can find this room ***
        active_game_rooms = cache.get("active_game_rooms", [])
        active_game_rooms.append(room_id)
        cache.set("active_game_rooms", active_game_rooms, timeout=600)

        return JsonResponse({
            "status": "matched", 
            "room_id": room_id, 
            # "player_data": [user_data, opponent_data]
        })

    else:
        # No opponent waiting, so add the current user to the waiting pool
        waiting_players.append(user_id)
        cache.set(MATCHMAKING_POOL_KEY, waiting_players, timeout=60)
        waiting_url = reverse("waiting_room", kwargs={"user_id": user_id})
        return JsonResponse({"status": "waiting", "user_id": user_id, "redirect": waiting_url})

def game_room(request, room_id):
    game_data = cache.get(f"game_room:{room_id}")
    if not game_data:
        return JsonResponse({"error": "Game not found"}, status=404)
    return render(request, "game_room.html", {"room_id": room_id, "players": game_data["players"]})

def leave_matchmaking(request):
    if request.method == "POST":
        # For leaving the matchmaking queue, we remove the user from waiting pool
        user_id = str(request.user.id) if request.user.is_authenticated else "Guest"
        waiting_players = cache.get(MATCHMAKING_POOL_KEY, [])
        if user_id in waiting_players:
            waiting_players.remove(user_id)
            cache.set(MATCHMAKING_POOL_KEY, waiting_players, timeout=60)

        # Also, if the user was already matched in a game room, remove them there.
        active_game_rooms = cache.get("active_game_rooms", [])
        for room_id in list(active_game_rooms):  # Use list() to iterate safely
            game_data = cache.get(f"game_room:{room_id}")
            if game_data and user_id in game_data["players"]:
                game_data["players"].remove(user_id)
                if not game_data["players"]:
                    cache.delete(f"game_room:{room_id}")
                    active_game_rooms.remove(room_id)
                    cache.set("active_game_rooms", active_game_rooms, timeout=600)
                else:
                    cache.set(f"game_room:{room_id}", game_data, timeout=600)
        return redirect(reverse("home_view"))
    return JsonResponse({"error": "Invalid request"}, status=400)

def check_match(request, user_id):
    # Use the stored active game rooms list instead of cache.keys()
    active_game_rooms = cache.get("active_game_rooms", [])
    for room_id in active_game_rooms:
        game_data = cache.get(f"game_room:{room_id}")
        if game_data and user_id in game_data["players"]:
            return JsonResponse({"status": "matched", "room_id": room_id})
    return JsonResponse({"status": "waiting"})

def waiting_room(request, user_id):
    return render(request, "waiting_room.html", {"user_id": user_id})