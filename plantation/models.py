from django.db import models
from django.contrib.auth.models import User
# Create your models here.
# plantation/models.py
class Plantation(models.Model):
    name = models.CharField(max_length=255)
    plantation_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='plantation_images/')
    description = models.TextField()

    def __str__(self):
        return self.name
