from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self',symmetrical=False , blank=True, related_name="user_followers")

    def count_followers(self):
        return self.followers.count()

    def count_following(self):
        return User.objects.filter(followers=self).count()

class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="emails")
    text = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("User", related_name="like_count")

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.email,
            "text": self.text,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "like_count": self.likes.count() 
        }

