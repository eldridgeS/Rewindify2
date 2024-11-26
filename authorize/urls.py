from django.contrib import admin
from django.urls import path, include

from . import views
from .views import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('signup/', SignUpView.as_view(), name="signup"),
    path('loginn/', views.loginn, name='loginn'),
    path('callback/', views.callback, name='callback'),
    path('refresh_token/', views.refresh_token, name='refresh_token'),
    path('spotify/playlists/', views.get_spotify_playlists, name='spotify_playlists'),
    path('link-success/', views.link_spotify_success, name='link_spotify_success'),
    path('wrappost/', views.wrappost, name='wrappost'),
    path('delete/', views.delete, name='delete'),

    path('password_change/', views.password_change, name='password_change'),

]
