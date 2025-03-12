from django.core.cache import cache

def get_game_room(username: str) -> str | None:
    """Return the first game room from the list of game rooms in the cache,
    in which the user is registered.
    """
    # Get all the active game rooms in the cache
    active_game_rooms = cache.get("active_game_rooms")

    if active_game_rooms == None:
        return None

    # Identify the first game room in the list, in which the user is.
    # Select this room as chat room for this user.
    player_names = []
    for game_room in active_game_rooms:
        room_content = cache.get(f"game_room:{game_room}")
        if room_content == None:
            continue
        player_data = room_content["player_data"]
        # Retrieve all the player names and add them to the list of players
        for player in player_data:
            player_names.append(player["username"])

        if username in player_names:
            return game_room
    else:
        return None


def get_players(game_room: str) -> list[str] | None:
    """Return the list of users currently in the game room.
    Example for the room content in the cache:
    {'players': ['3', '2'],
    'player_data': [
        {'id': 3, 'username': 'Ole', 'image': <ImageFieldFile: user_profile_images/profile_placeholder.jpeg>, 'average': 2.25},
        {'id': 2, 'username': 'kilian', 'image': <ImageFieldFile: user_profile_images/0kIPXTKI_400x400.jpg>, 'average': 19.8}]
        }
    """

    active_game_rooms = cache.get("active_game_rooms")
    if game_room not in active_game_rooms:
        return None

    room_content = cache.get(f"game_room:{game_room}")
    if room_content == None:
        return None

    player_data = room_content["player_data"]
    player_names = []
    for player in player_data:
        player_names.append(player["username"])

    return player_names

def delete_question_from_questions(question: str, questions: list[dict]) -> list[dict]:
    """Delete the last question and answers from the list of questions created by Ai
    Args:
        question (str): _Question previously asked to players_
        questions (list[dict]): list of questions of this form:
        [   {'question': "Which planet in our solar system is known as the 'Red Planet'?",
            'A': 'Earth',
            'B': 'Jupiter',
            'C': 'Saturn',
            'D': 'Mars',
            'correct_answer': 'D'},
            {'question':
            'What is the largest living structure on Earth?',
            'A': 'The Great Wall of China',
            'B': 'The Great Barrier Reef',
            'C': 'The Amazon Rainforest',
            'D': 'The Grand Canyon',
            'correct_answer': 'B'}
            ]
    Returns:
        list[dict]: List of dictionary with one item less corresponding to the passed quesion.
    """
    for index, question_item in enumerate(questions):
        if question_item["question"] == question:
            del questions[index]
    return questions