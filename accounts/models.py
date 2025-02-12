from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):

    image = image = models.ImageField(upload_to="user_profile_images/",default= "/static/assets/profile_placeholder.jpeg") 
    stars = models.IntegerField(null=True)




