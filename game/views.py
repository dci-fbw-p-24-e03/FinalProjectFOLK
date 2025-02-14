from django.shortcuts import render
from .ai import  get_question

# Create your views here.

def game_view(request):
    
    return render(request, "game.html")


def game_start(request, *args, **kwargs):
    print("game start")
    
    player = request.user.username
    request.session["player"] = {player: 0}
    topic = request.POST.get("topic")
    request.session["topic"] = topic
    difficulty = request.POST.get("difficulty")
    request.session["difficulty"] = difficulty
    question = get_question(topic=topic, difficulty=difficulty)
    if request.session.get("questions") == None:
        request.session["questions"] = [question]  # Store in session (must be serializable)
    else:
        questions = request.session["questions"]
        questions.append(question)
        request.session["questions"] = questions
    
    score = request.session["player"][f"{player}"]
    context = question | {"score": score}
    return render(request, "game-start.html", context)

def game_flow(request, *args, **kwargs):
    print("game flow")
   
    previous_questions = request.session.get("questions")
    difficulty = request.session.get("difficulty")
    topic = request.session.get("topic")
    correct_answer = previous_questions[-1]["correct_answer"]
    submitted_answer = request.POST.get("options")
    print("correct answer:", correct_answer)
    print("submitted answer: ", submitted_answer)
    if correct_answer == submitted_answer:
        player = request.user.username
        score = request.session["player"][f"{player}"]
        score += 5
        request.session["player"][f"{player}"] = score
        print("points: ",score, request.session["player"][f"{player}"])
        #print("previous questions", previous_questions)
   
    not_questions = [question["question"] for question in previous_questions]
    print("not_questions: ", not_questions)
    question = get_question(topic=topic, difficulty=difficulty, not_questions=not_questions)
    questions = request.session["questions"]
    questions.append(question)
    request.session["questions"] = questions
    player = request.user.username
    score = request.session["player"][f"{player}"]
    context = question | {"score": score}
    return render(request, "game-flow.html", context)

        
        
