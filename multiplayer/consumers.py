from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from django.core.cache import cache
from .cache_functions import get_game_room, delete_question_from_questions
from game.ai import get_question
from datetime import datetime

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

        #print("received data: ", data)

################################ The Chat ###################################

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

################################## Get ready to Play #######################################

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

        #received data:  {'topic': 'sport', 'theme': 'AI-Quiz', 'difficulty': 'easy',
        # Saving Choices ( theme,topic,difficulty ) in our cache:

            chooser = self.scope["user"]

            chosen_topic = data.get("topic")
            chosen_theme = data.get("theme")
            chosen_difficulty = data.get("difficulty")
            #print("choices:",chosen_difficulty,chosen_theme,chosen_topic)

            key= f"{chooser}_choices" 
            data = {
                        "topic":chosen_topic,
                        "difficulty":chosen_difficulty,
                        "theme": chosen_theme
                    }
            
            game_room = cache.get(f"game_room:{self.room_name}")
            game_room[key] = data
            cache.set(f"game_room:{self.room_name}", game_room)
            # print(game_room)
            
            if chosen_theme == "Space - Theme":
                chosen_theme = "space_arena"
            
            context = f'<body id="theme" name="theme" class={chosen_theme}>'
            await self.send(context)
            
            # <body class="{% if theme == 'Space - Theme' %}space_arena{% elif theme == 'Elder - World' %}elder_arena{% else %}standard_arena{% endif %}"></body>>




        # get the game room 

            #game_room["theme"] = 





            # Get the questions for the game and save them in the cache!!
            print(game_room)
            # Only generate questions if they don't exist yet and all players are ready.
            if game_room.get("questions") is None and game_room.get("ready") == len(game_room.get("players", [])):
                questions = []
                players = game_room.get("players", [])  # e.g. ['6', '4']
                player_data = game_room.get("player_data", [])
                
                # Generate 2 rounds of questions, alternating between players.
                for i in range(2):
                    # Build list of already-used question texts to avoid duplicates
                    not_questions = [q["question"] for q in questions] if questions else []
                    
                    topic = None
                    difficulty = None
                    if players:
                        current_player_id = players[i % len(players)]
                        # Look up the corresponding username without changing case (assuming it was saved that way)
                        player_username = None
                        for pdata in player_data:
                            if str(pdata.get("id")) == current_player_id:
                                player_username = pdata.get("username").strip()
                                break
                        if player_username:
                            key = f"{player_username}_choices"
                            player_choices = game_room.get(key, {})
                            topic = player_choices.get("topic")
                            difficulty = player_choices.get("difficulty")
                            print("Using choices for player", player_username, ":", topic, difficulty)
                        else:
                            print("No matching username for player id:", current_player_id)
                    else:
                        print("No players found in game_room")
                    
                    # Call get_question with the alternating player's topic and difficulty.
                    question = get_question(not_questions=not_questions, topic=topic, difficulty=difficulty)
                    questions.append(question)
                    print(question)
                
                game_room["questions"] = questions
                cache.set(f"game_room:{self.room_name}", game_room)
            game_room = cache.get(f"game_room:{self.room_name}")

############################### All Users are ready to Play ########################################

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

############################### Record the beginning of a question round for each User ########################################

        # Record the time that the multi_play page has been loaded
        round = data.get("round")
        if round != None:
            
            # Record time, when the game starts
            round_start = datetime.now()
            # Transform datetime object into string
            pattern = "%d/%m/%Y, %H:%M:%S%f"
            round_start = round_start.strftime(pattern)
            # Store start time of user in the Cache
            user = self.scope["user"]
            user = str(user)
            
            print(f"{user}'s round start: ", round_start)
            if game_room.get(f"{user}_round_start") == None:
                game_room[f"{user}_round_start"] = round_start
            else:
                game_room[f"{user}_round_start"] = round_start
            game_room_name = f"game_room:{self.room_name}"
            cache.set(game_room_name, game_room)


        # get the answer given by the user (input name=options in multi_play.html), get it
        # from the scope (data); get the username, who has chosen the answer; get the value for
        # the game_room_name key to get the corresponding game_room from the cache.
        answer = data.get("options")
        user = str(self.scope["user"])
        game_room_name = f"game_room:{self.room_name}"
        game_room = cache.get(f"game_room:{self.room_name}")
        # if a user has actually chosen an answer 
        if answer:
            
            # Record the moment in time, in which the user chose an answer
            choice_time = datetime.now()
            
            print("choice time: ", choice_time)
            
            # Retrieve the round start from the cache
            round_start = game_room.get(f"{user}_round_start")
            
            print("cached start of the round: ", round_start)
            
            if round_start != None:
                #print("round start retrieved: ", round_start)
                # Transform the round start into a datetime object
                pattern = "%d/%m/%Y, %H:%M:%S%f"
                round_start = datetime.strptime(round_start, pattern)
        
                # Calculate the time difference in seconds
                time_difference = choice_time - round_start
                time_difference = time_difference.total_seconds()
        
            else:
                time_difference = 5
                
            # make sure the key "answers" exists in the game_room dict. if it doesn't exist, create 
            # it with an emtpy dict as value
        
            if "answers" not in game_room:
                game_room["answers"] = {}

            # every user needs to have a list to save their answers. If it doesn't exist in the
            # game_room dict already, create it. It is saved in the answers dict inside the game_room
            # dict as the value of the key "user" (username)
            if user not in game_room["answers"]:
                game_room["answers"][user] = []

            # Check, if the key "questions" exists in the game_room dict and if the value to the 
            # key (the list of questions) is not empty
            if "questions" in game_room and game_room["questions"]:
                current_question = game_room["questions"][-1]  # if there is a question (or more) in
                # in the list, get the last question in the list, because it is the currently asked
                # one

                # Determine if the answer is correct or not (True or False)
                correct_answer = current_question["correct_answer"]
                is_correct = (answer == correct_answer)

                # save a dictionary consisting of the current question, correct answer and answer
                # chosen by the user in the list connected to the username inside the answer dict 
                # inside the game_room dict
                game_room["answers"][user].append({
                    "question": current_question["question"],
                    "correct_answer": correct_answer,
                    "player_answer": answer,
                    "correct": is_correct,
                    "time": time_difference,
                })
                
                #print("game room with timing: ", game_room)

                # print(game_room["answers"])
                
                # save everything in the cache
                cache.set(game_room_name, game_room)
                
                 # Display the user' choice in the html:
                 
                tag = f'<label id={answer} class="radio-button" style="background-color: #007bff; color: #eaf0ec;">'
                tag +=  f'<input name="options" type="radio" id="option_3" value="C" /> {current_question[answer]} </label>'
                
                await self.send(tag)
                    
        # If both players see the results page, then delete the last question that was previously displayed
        # from the cache, such that the next question will be displayed when the game returns to the
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
        

############################################ Game Over #############################################

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
            # Check whether all the players in the game room have ended the game.
            if len(game_room.get("players")) == game_room.get("game_over"):
                # Wait 10 seconds before the game room is deleted for sure
                # (just in case a user needs a bit more time and switch to the multi_play_over html)
                await asyncio.sleep(10)  

                # Make sure the game room is not needed any longer
                game_room = cache.get(f"game_room:{game_room_name}")
                if game_room and len(game_room.get("players")) == game_room.get("game_over"):
                    cache.delete(f"game_room:{game_room_name}")

    async def chat_message(self, event):
        # This method will be called when a message is received from the group
        # This method further defines the event type of the message as "chat_message"
        message = event["message"]

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({"message": message}))
