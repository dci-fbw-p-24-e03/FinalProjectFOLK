from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.core.cache import cache
from .cache_functions import get_game_room, delete_question_from_questions
from game.ai import get_question

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

        print("received data: ", data)
        # Retrieve the chat message
        message = data.get("chat_message")
        # Identify the user who chatted
        chatter = self.scope["user"]
        # Retrieve the game room used by the players
        game_room = cache.get(f"game_room:{self.room_name}")

        #print("user", chatter, "in game room", self.room_name)

        # If you received a chat message then post it:
        if message != None:

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
            # This message is only sent to the use who chatted.
            await self.send('<input id="myInput" name="chat_message">')

        # If the player pressed the play button:
        play = data.get("play")
        if play != None:
            # Send a message to the player asking him to wait for his opponent to respond in kind
            context = f"<div id='play' name='play'> Wait for Opponent</div>"
            await self.send(context)

            # Save the players choice in the cache.
            if game_room.get("ready") == None:
                game_room["ready"] = 1
                cache.set(f"game_room:{self.room_name}", game_room)
            else:
                game_room["ready"] += 1
                cache.set(f"game_room:{self.room_name}", game_room)

            # Get the questions for the game and save them in the cache!!

            if game_room.get("questions") == None:
                questions = []
                for index in range(2):
                    not_questions = []
                    if questions != []:
                        for question in questions:
                            not_questions.append(question["question"])
                    question = get_question(not_questions=not_questions)
                    questions.append(question)

                game_room["questions"] = questions
                cache.set(f"game_room:{self.room_name}", game_room)
            game_room = cache.get(f"game_room:{self.room_name}")

        # If all the players in the game room have chosen to play
        # then let the game begin

        if len(game_room.get("players")) == game_room.get("ready"):
            #print("Two players in a playroom: let's play!")
            # render an new page for playing by sending an htmx tag
            # to all participants in the front end simultaneously, which will
            # swap the content of the website

            context = "<div id='lets_play' hx-get='/multi_play' hx-target='#swap-multi_play' hx-trigger='load'> </div>"
            # Send the letsplay div to all the members of the chat group simultaneously.
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",  # The event type for the message
                    "message": context,  # The message content
                },
            )


        # If both players see the results page, then delete the last question that was previously displayed
        # from the cache, such that the next question will be displayed when, the game returns to the
        # multiplay page.
        # The results message is sent from the results room only:
        current_question=data.get("results")
        user = self.scope["user"]
        user = str(user)
        game_room_name = get_game_room(user)
        game_room = cache.get(f"game_room:{game_room_name}")
        questions = game_room.get("questions")
        remaining_questions=delete_question_from_questions(current_question, questions)
        #print(f"This is the remaining question: {remaining_questions}")
        game_room["questions"] = remaining_questions
        cache.set(f"game_room:{self.room_name}", game_room)
        #print(f"This ist the game room after deleting the last question: {game_room}")
        
        # Delete the Game Room, if the game is over for all the users:
        # If you received a message from a player that he has reached the end of the game
        # from the front end
        game_over = data.get("game_over")
        if game_over != None:
            # Check if he is the first player who ended the game
            if game_room.get("game_over") == None:
                # If he is the frist player, then create the key game_over in the game_room and
                # mark that a first player has ended the game.
                game_room["game_over"] = 1
                cache.set(f"game_room:{self.room_name}", game_room)
            else:
                # If he is not the first player who ended the game, then add 1 to the number of players
                # who have come to the end of the game.
                game_room["game_over"] += 1
                cache.set(f"game_room:{self.room_name}", game_room)
            # Check whether all the players in the game room have ended the game.
            if len(game_room.get("players")) == game_room.get("game_over"):
                # Delete the game room, when the  game has come to an end.
                cache.delete(f"game_room:{game_room_name}")
        
        
        
    async def chat_message(self, event):
        # This method will be called when a message is received from the group
        # This method further defines the event type of the message as "chat_message"
        message = event["message"]

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({"message": message}))
