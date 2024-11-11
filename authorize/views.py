from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from django.http import HttpResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import redirect, render
import requests
import json
import base64
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import redirect, render
from django.http import HttpResponse

from .forms import CustomUserCreationForm
from .models import UserSpotifyProfile
import logging

def spotify_login(request):
    sp_oauth = SpotifyOAuth(client_id="e2f1ae44b7714b3a904b51b818360e71",
                            client_secret="b2152296189648798ab82d40b3f1bfd2",
                            redirect_uri="http://localhost:8000/authorize/spotify/callback/",
                            scope="user-library-read user-top-read user-read-email playlist-read-private")

    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


def sp(request):
    return render(request, 'registration/spoterpy.html')

# Set up logging
logger = logging.getLogger(__name__)

def spotify_callback(request):
    sp_oauth = SpotifyOAuth(client_id="e2f1ae44b7714b3a904b51b818360e71",
                            client_secret="b2152296189648798ab82d40b3f1bfd2",
                            redirect_uri="http://localhost:8000/authorize/spotify/callback/")

    code = request.GET.get('code')
    if not code:
        logger.error("Authorization code not found")
        return HttpResponse("Authorization code not found", status=400)

    try:
        # Manually send request to get access token
        auth_str = f"{sp_oauth.client_id}:{sp_oauth.client_secret}"
        b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": sp_oauth.redirect_uri
        }
        response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

        # Log the entire response
        logger.info(f"Spotify token response status: {response.status_code}")
        logger.info(f"Spotify token response text: {response.text}")

        # Check if response is successful
        if response.status_code != 200:
            logger.error(f"Failed to obtain access token: {response.text}")
            return HttpResponse(f"Failed to obtain access token: {response.text}", status=response.status_code)

        # Parse the token information
        token_info = response.json()

    except Exception as e:
        logger.error(f"Failed to obtain access token: {e}")
        return HttpResponse(f"Failed to obtain access token: {str(e)}", status=400)

    access_token = token_info.get('access_token')
    refresh_token = token_info.get('refresh_token')

    sp = spotipy.Spotify(auth=access_token)
    try:
        user_profile = sp.current_user()
        spotify_id = user_profile['id']  # Get the Spotify user ID
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        return HttpResponse(f"Failed to get user profile: {str(e)}", status=400)

    user = request.user

    # Store tokens in the database
    profile, created = UserSpotifyProfile.objects.update_or_create(
        user=user,
        defaults={'spotify_id': spotify_id, 'access_token': access_token, 'refresh_token': refresh_token}
    )

    return redirect('link_spotify_success')


def refresh_spotify_token(request):
    refresh_token = request.session.get('spotify_refresh_token')
    if not refresh_token:
        return redirect('spotify_login')  # Redirect to login if refresh token is missing

    sp_oauth = SpotifyOAuth(client_id="e2f1ae44b7714b3a904b51b818360e71",
                            client_secret="b2152296189648798ab82d40b3f1bfd2",
                            redirect_uri="http://localhost:8000/authorize/spotify/callback/")

    token_info = sp_oauth.refresh_access_token(refresh_token)
    request.session['spotify_token'] = token_info['access_token']


def get_spotify_playlists(request):
    access_token = request.session.get('spotify_token')
    if not access_token:
        return redirect('spotify_login')  # Redirect to login if token is missing

    sp = spotipy.Spotify(auth=access_token)
    playlists = sp.current_user_playlists()

    return render(request, 'registration/show_playlists.html', {'playlists': playlists['items']})


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def link_spotify_success(request):
    return render(request, 'registration/link_spotify_success.html')
