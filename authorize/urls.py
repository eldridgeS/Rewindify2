from django.contrib import admin
from django.urls import path, include

from . import views
from .views import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', SignUpView.as_view(), name="signup"),
    path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
    path('spotify/playlists/', views.get_spotify_playlists, name='spotify_playlists'),
    path('link-success/', views.link_spotify_success, name='link_spotify_success'),
    path('sp/', views.sp, name='sp'),

]
