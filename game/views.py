from django.shortcuts import render
from .ai import  get_question

# Create your views here.

def game_view(request):
    
    return render(request, "game.html")


def game_update(request, *args, **kwargs):
    not_questions = []
    
    topic = request.POST.get("topic")
    difficulty = request.POST.get("difficulty")
    questions = get_question(topic=topic, difficulty=difficulty)
    request.session["questions"] = questions  # Store in session (must be serializable)
    return render(request, "game-update.html", questions, not_questions)

def game_flow(request, *args, **kwargs):
    index = 0
    while index < 10:
        index +=1
        previous_question = request.session.get("questions")["question"]
        choice = request.POST.get("options")
        questions = get_question(not_questions=[previous_question,])
        print("previous question", previous_question)
        print("choice", choice)
        return render(request, "game-update.html", questions)
        
        
    else:
        index = 0
        return render("game over")
        
        
       