from django.urls import re_path, path
from . import views

urlpatterns = [
    path('', views.remote_game, name='remote-game'),

]