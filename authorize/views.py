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
import base64
import json
import random
import string
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session

# Spotify API and app credentials
CLIENT_ID = settings.SPOTIFY_CLIENT_ID
CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET
REDIRECT_URI = settings.SPOTIFY_REDIRECT_URI
STATE_KEY = 'spotify_auth_state'




def generate_random_string(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def loginn(request):
    # Generate a random state string to prevent CSRF attacks
    state = generate_random_string()
    request.session[STATE_KEY] = state

    # Spotify authorization URL
    scope = 'user-read-private user-read-email user-top-read user-library-read'
    auth_url = f'https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}&scope={scope}'

    return redirect(auth_url)

def callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if not code:
        return HttpResponse("No authorization code received", status=400)

    # Exchange the authorization code for an access token
    auth = (settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    token_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(token_url, data=data, headers=headers, auth=auth)

    if response.status_code != 200:
        return HttpResponse("Error fetching token", status=500)

    token_data = response.json()
    access_token = token_data.get('access_token')

    if not access_token:
        return HttpResponse("Failed to retrieve access token", status=500)

    # Save access token to session
    request.session['spotify_token'] = access_token

    # Fetch user profile data from Spotify
    user_profile_url = 'https://api.spotify.com/v1/me'
    user_profile_headers = {
        'Authorization': f'Bearer {access_token}',
    }
    user_profile_response = requests.get(user_profile_url, headers=user_profile_headers)

    if user_profile_response.status_code != 200:
        return HttpResponse("Error fetching user profile", status=500)

    user_profile = user_profile_response.json()

    # Fetch playlists
    sp = spotipy.Spotify(auth=access_token)
    playlists = sp.current_user_playlists()
    top_tracks = sp.current_user_top_tracks(limit=5)
    top_artists = sp.current_user_top_artists(limit=5)
    total_minutes = 0  # Variable to store total listening time in minutes

    genres = set()  # Using a set to avoid duplicates
    for artist in top_artists['items']:
        artist_info = sp.artist(artist['id'])  # Get detailed artist information
        genres.update(artist_info['genres'])

    for track in top_tracks['items']:
        track_duration_ms = track['duration_ms']
        track_duration_minutes = track_duration_ms / 1000 / 60  # Convert milliseconds to minutes
        total_minutes += track_duration_minutes

    # Render the user profile and playlists in the template
    return render(request, 'registration/logged_in.html', {
        'profile': user_profile,
        'playlists': playlists['items'],
        'top_tracks': top_tracks['items'] if top_tracks['items'] else None,  # If empty, pass None
        'top_artists': top_artists['items'] if top_artists['items'] else None,  # If empty, pass None
        'genres': list(genres) if genres else None,  # If no genres, pass None
        'total_minutes': round(total_minutes, 2) if total_minutes else None,  # Round total minutes
    })
@csrf_exempt
def refresh_token(request):
    refresh_token = request.POST.get('refresh_token')

    # Prepare token refresh request
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode('utf-8'),
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        tokens = response.json()
        return JsonResponse(tokens)
    else:
        return JsonResponse({'error': 'failed_to_refresh_token'}, status=400)


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




