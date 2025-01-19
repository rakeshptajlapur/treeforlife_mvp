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
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when the object is created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set whenever the object is updated

    def __str__(self):
        return self.name


class Timeline(models.Model):
    plantation = models.ForeignKey(Plantation, on_delete=models.CASCADE, related_name='timelines')
    activity_date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return f"{self.plantation.name} - {self.activity_date}: {self.description[:30]}"
    


class Comment(models.Model):
    timeline = models.ForeignKey(Timeline, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Who made the comment
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.timeline.activity_date}"

    class Meta:
        ordering = ['-created_at']  # Show latest comments first

