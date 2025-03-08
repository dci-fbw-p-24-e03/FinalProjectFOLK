from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.core.cache import cache


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        # Identify the user connecting to the websocket
        user = self.scope["user"]
        user = str(user)

        # Identify the first game room, in which the user is registered.
        self.room_name = get_game_room(user)

        # Create a chat group on the basis of the game room
        self.room_group_name = f"chat_{self.room_name}"

        # Join the group
        await self.channel_layer.group_add(
            self.room_group_name,  # Group name
            self.channel_name,  # Unique connection channel
        )
        # Accept the WebSocket connection
        await self.accept()

    async def receive(self, text_data):
        # Turn received data into a python readable dictionary
        data = json.loads(text_data)
        # Retrieve the message
        message = data.get("chat_message", "No message received")
        
        # Identify the user who chatted
        chatter = self.scope["user"]
        
        # Create the response, which will replace the div with the id 'chat_message'
        # The chat content is automatically inserted at the end of the div. The residual content remains.
        context = f"<div id='chat_message' hx-swap-oob='beforeend'> <p>{chatter}: {message}</p> </div> "

        # Send the chat to all the members of the chat group.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",  # The event type for the message
                "message": context,  # The message content
            },
        )

        # Clear the text from the input field by replacing it with an identical input tag:
        await self.send('<input id="myInput" name="chat_message">')

    async def chat_message(self, event):
        # This method will be called when a message is received from the group
        # This method further defines the event type of the message as "chat_message"
        message = event["message"]

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({"message": message}))


def get_game_room(username: str) -> str | None:
    """Returng the first game room from the list of game rooms in the cache,
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
    """ Return the list of users currently in the game room.
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
