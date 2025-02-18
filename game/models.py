from django.db import models
from accounts.models import CustomUser

# Create your models here.

     
class Questions(models.Model):
    question = models.CharField(max_length=1000)
    player = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        max_questions = 50  # Set your desired limit
        question_count = Questions.objects.filter(player=self.player).count()
        if question_count >= max_questions:
            # Get the 10 oldest questions for this player and delete them
            oldest_questions = Questions.objects.filter(player=self.player).order_by('created_at')[:10]
            oldest_questions.delete()

        super().save(*args, **kwargs)  # Save the new question

""" 
class Game(models):
    
    topic = models.CharField(max_length=100)
    difficulty =  models.CharField(max_length=30)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="Player")
    questions = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name="Questions") """