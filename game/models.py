from django.db import models

# Create your models here.


""" class Player(models):
     name = models.CharField(max_length=100)
     points = models.IntegerField(default=0)
     image = models.ImageField()
     
class Questions(models):
    question = models.CharField(max_length=1000)

class Game(models):
    
    topic = models.CharField(max_length=100)
    difficulty =  models.CharField(max_length=30)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="Player")
    questions = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="Questions") """