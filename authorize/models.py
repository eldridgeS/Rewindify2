from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField

class SpotifyWrap(models.Model):
    songs = JSONField()
    artists = JSONField()
    image = models.CharField(max_length=255)

    def __str__(self):
        return self.image

class UserSpotifyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    profile = models.ForeignKey(SpotifyWrap, on_delete=models.CASCADE, related_name='user_data')

    def __str__(self):
        return self.user.username

# class Wrap(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wraps")
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.title} - {self.user.username}"