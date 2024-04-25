from django.urls import path
from . import views

urlpatterns = [
    path('result', views.game_results, name='game-result'),
]