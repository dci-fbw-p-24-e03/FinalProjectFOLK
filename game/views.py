from django.shortcuts import render
from .ai import get_question
from .models import Questions
from accounts.models import CustomUser
# Create your views here.


def game_view(request):
    """Render Opening Page of Game

    Args:
        request (get): /game

    Returns:
        _html_: html for displaying the opening page of the game

    Summary:
        game.html comprises the swap target called "swap-container" (hx-target = "#swap-container").
        The html code within the  <div id="swap-container"> is completely replaced with new html code
        once <button type="submit">Choose</button> is pressed. Pressing the choose button issues a
        post request (hx-post="/game-start" ) to the URL /game-start. This post request is processed
        by the next view game_start, which replaces the html code in the div <div id="swap-container">.

    """

    # Delete questions and information from the session left over from an interrupted game

    if request.session.get("questions") != None:
        del request.session["questions"]
    if request.session.get("score") != None:
        del request.session["score"]
    if request.session.get("topic") != None:
        del request.session["topic"]
    if request.session.get("difficulty") != None:
        del request.session["difficulty"]

    return render(request, "game.html")


def game_start(request):
    """Game start displays the first question of the game

    Args:
        request (post): /game-start
                        The post request comprises the name of the user, the topic chosen for the game and
                        the level of difficulty.

    Returns:
        _html_: html for displaying the question and possible answers within the <div id="swap-container">
                in the game.html

    Summary:
        game.html is updated with the html code from game_start within <div id="swap-container">.
        The first question and four possible answers are displayed to the user in a form. The user
        can chose one possible answer and submit his answer, whereby a post request hx-post="/game-flow"
        is transmitted to the start_result view. The target of this htmx request is again the swap-container.
    """

    # Previous questions is a list of dictionaries, each dictionary comprising a previous question,
    # the possible answers and the correct answer.
    previous_questions = request.session.get("questions")
    
    # Retrieving the questions already asked by the user and stored in the Questions database
    user_pk = request.user.pk
    old_questions_iterator = Questions.objects.filter(player=user_pk)
    old_questions = [question.question for question in old_questions_iterator]

    if previous_questions == None or len(previous_questions) == 0:
        not_questions = []
        selected_topic = request.POST.get("topic") # Value from dropdown
        custom_topic = request.POST.get("custom-topic") # Value from custom input field
        topic=""
        if selected_topic == None:
            # The user did NOT choose anything from the dropdown
            # => use whatever was typed in the custom input field
            topic = custom_topic
        else:
            # The user did NOT type a custom topic (they left the placeholder?)
            # => use the dropdown topic
            topic = selected_topic
        difficulty = request.POST.get("difficulty")
    
        # Add the posted information to the "session". 'request.session' is a dictionary for storing information
        # used during the course of the game. The information is stored in a cooky in the front end.

        request.session["score"] = 0
        request.session["topic"] = topic
        request.session["difficulty"] = difficulty

    # If the game has been played for 10 rounds then set the sessions data back to nill
    # and render the game-over.html last round!
    elif len(previous_questions) >= 10:
        
        # store the questions asked during this game in the database
        for question in previous_questions:
            player = CustomUser(pk=user_pk)
            database_objet = Questions(question=question["question"], player=player)
            database_objet.save()

        score = request.session.get("score")
        not_questions = []
        request.session["questions"] = []
        request.session["score"] = 0
        if request.session.get("topic") != None:
            del request.session["topic"]
        if request.session.get("difficulty") != None:
            del request.session["difficulty"]

        context = {
            "score": score,
        }

        return render(request, "game-over.html", context)

    # Retrieve the topic of the game as well as the game difficulty from
    # the post request forwarded to the present view from game start first round

    # If a question has been asked previously and the game is ongoing, then
    # retrieve the difficulty, topic and previous questions from the session dictionary

    else:
        difficulty = request.session.get("difficulty")
        topic = request.session.get("topic")
        # Creating a list of questions not to be asked by ai.py
        not_questions = [question["question"] for question in previous_questions]
        # adding the old questions to the list of not questions
        not_questions.extend(old_questions)
        

    # Get the question dictionary comprising the question, possible answers and correct answer using
    # the get_question function defined in ai.py
    question = get_question(
        topic=topic,
        difficulty=difficulty,
        not_questions=not_questions,
    )
    
    # Add the question dictionary to the session. The value corresponding to the key "questions" comprises
    # a list of all the questions that have been asked before.
    if request.session.get("questions") == None:
        # Create the questions list if it does not exist yet and add the first question
        request.session["questions"] = [question]
    else:
        # Retrieve the list of asked questions
        questions = request.session["questions"]
        # Append the current question to this list
        questions.append(question)
        # Replace the list of questions in the sessions dictionary with the updated list.
        request.session["questions"] = questions

    # Get the current score of the player from the sessions dictionary
    score = request.session["score"]

    # Create a context dictionary by merging the dictionaries question and {"score": score}
    # into a single dictionary
    context = question | {"score": score}
    # Display the question and possible answers to the player in the game.html by replacing
    # the content within <div id="swap-container"> with the html of game-start.html
    return render(request, "game-start.html", context)


def start_result(request):
    """Display whether the first question was answered correctly

    Args:
        request (post): /start-result
                        The post request comprises the user's choice among the four  possible answers.
    Summary:
        game.html is updated with the html code from start-result within <div id="swap-container">.
        The container comprises the correct answer as well as the resulting score of the user.

    """
    previous_questions = request.session.get("questions")
    last_question = previous_questions[-1]
    correct_answer = last_question["correct_answer"]
    submitted_answer = request.POST.get("options")

    score = request.session.get("score")
    result = ""
    if correct_answer == submitted_answer:
        score += 5
        request.session["score"] = score
        result = "correct"
    else:
        result = "wrong"

    correct_answer = last_question[correct_answer]
    correct_option = last_question["correct_answer"]
    

    context = last_question | {"score": score,
                               "submitted_answer" : submitted_answer,
                               "correct_option" : correct_option}  
    print(correct_answer)
    print(submitted_answer)

    return render(request, "start-result.html", context)
