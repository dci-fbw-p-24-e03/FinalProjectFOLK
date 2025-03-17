from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.cache import cache
from django.urls import reverse
import uuid
from accounts.models import CustomUser  # Import User model
from . cache_functions import get_game_room, get_players
from game.ai import get_explanations

# Create your views here.
MATCHMAKING_POOL_KEY = "matchmaking_pool"


def join_matchmaking(request):
    user_id = (
        str(request.user.id) if request.user.is_authenticated else str(uuid.uuid4())
    )
    user_name = (
        request.user.username
        if request.user.is_authenticated
        else f"Guest {user_id[:4]}"
    )  # Use guest name if not authenticated

    waiting_players = cache.get(MATCHMAKING_POOL_KEY, [])

    # If the user is already in the pool, no need to add again, just send them to the waiting room
    if user_id in waiting_players:
        waiting_url = reverse("waiting_room", kwargs={"user_id": user_id})
        return JsonResponse(
            {"status": "waiting", "user_id": user_id, "redirect": waiting_url}
        )

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
            "image": user.image,
            "average": user.average_stars_per_game,
        }

        # Update the cache with the new state of the pool
        cache.set(MATCHMAKING_POOL_KEY, waiting_players, timeout=60)

        # Create a new game room for the matched players, including full user data
        room_id = str(uuid.uuid4())  # New unique game room id
        cache.set(
            f"game_room:{room_id}",
            {
                "players": [user_id, opponent_id],
                "player_data": [user_data, opponent_data],
            },
            timeout=120,
        )

        # *** NEW: Update active_game_rooms so that check_match can find this room ***
        active_game_rooms = cache.get("active_game_rooms", [])
        active_game_rooms.append(room_id)
        cache.set("active_game_rooms", active_game_rooms, timeout=600)

        return JsonResponse(
            {
                "status": "matched",
                "room_id": room_id,
                # "player_data": [user_data, opponent_data]
            }
        )

    else:
        # No opponent waiting, so add the current user to the waiting pool
        waiting_players.append(user_id)
        cache.set(MATCHMAKING_POOL_KEY, waiting_players, timeout=60)
        waiting_url = reverse("waiting_room", kwargs={"user_id": user_id})
        return JsonResponse(
            {"status": "waiting", "user_id": user_id, "redirect": waiting_url}
        )


def game_room(request, room_id):
    game_data = cache.get(f"game_room:{room_id}")
    if not game_data:
        return JsonResponse({"error": "Game not found"}, status=404)

    # Retrieve users from the database
    player_ids = game_data["players"]

    # Create a list of players from the database.
    players = []
    for player_id in player_ids:
        player = CustomUser.objects.get(id=player_id)
        players.append(player)

    return render(request, "game_room.html", {"room_id": room_id, "players": players})


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

def multi_play(request):
    user = request.user
    username = str(user)
    game_room_name = get_game_room(username)
    players = get_players(game_room=game_room_name)
    for player in players:
        if player != username:
            opponent_name = player
    opponent = CustomUser.objects.get(username=opponent_name)
    game_room = cache.get(f"game_room:{game_room_name}")
    questions = game_room["questions"]
    if questions != []:
        question = questions[-1]
        context = { "user": user,
                   "opponent": opponent,
                "username": username,
                "players": players,
                "game_room_name": game_room_name,
                "question": question["question"],
                "A": question["A"],
                "B": question["B"],
                "C": question["C"],
                "D": question["D"]
                }
        return render(request, "multi_play.html", context)
    else:
        player_answers = game_room.get("answers", {}).get(username, [])
        wrong_answers=[]
        for answer in player_answers:
            if answer["correct"]==False:
                wrong_answer={
                    "question":answer["question"], 
                    "correct_answer":answer["correct_answer"],
                    "correct_answer_text":answer["correct_answer_text"],
                    "player_answer_text":answer["player_answer_text"],
                    }
                wrong_answers.append(wrong_answer)
        explanations=get_explanations(
            wrong_answers
        )
        for wrong_answer in wrong_answers:
            question_text = wrong_answer["question"]
            wrong_answer["explanation"] = explanations.get(
                question_text, "No explanation available."
            )
        
        context = {
            "user": user,
            "wrong_answers": wrong_answers,
            "opponent": opponent,
            "username": username,
            "players": players,
            "game_room_name": game_room_name,
        }
        return render(request, "multi_play_over.html", context)

def results(request):
    user = request.user
    username = str(user)
    game_room_name = get_game_room(username)
    players = get_players(game_room=game_room_name)    
    for player in players:
        if player != username:
            opponent_name = player
    opponent_object = CustomUser.objects.get(username=opponent_name)
    game_room = cache.get(f"game_room:{game_room_name}")
    questions = game_room["questions"]
    current_question = questions[-1] if questions else None
    player_answers = game_room.get("answers", {}).get(username, [])
    opponent_answers=game_room.get("answers", {}).get(opponent_name, [])
    last_answer = player_answers[-1] if player_answers else None
    last_answer_opponent=opponent_answers[-1] if opponent_answers else None
    if questions != []:
        question = questions[-1]
        context = {
            "user": user,
            "opponent": opponent_object,
            "players": players,
            "question": current_question["question"] if current_question else "N/A",
            "A": current_question["A"] if current_question else "",
            "B": current_question["B"] if current_question else "",
            "C": current_question["C"] if current_question else "",
            "D": current_question["D"] if current_question else "",
            "answer": current_question["correct_answer"] if current_question else "",
            "player_answer": last_answer["player_answer"] if last_answer else "N/A",
            "opponent_answer":last_answer_opponent["player_answer"] if last_answer_opponent else "N/A",
            "is_correct": last_answer["correct"] if last_answer else False,
            "is_correct_opponent": last_answer_opponent["correct"] if last_answer_opponent else False,
        }
        if questions!=[]:
            return render(request, "results.html", context)
