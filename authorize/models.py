from django.db import models
from django.contrib.auth.models import User

class UserSpotifyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username
