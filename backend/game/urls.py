from django.urls import path
from . import views

urlpatterns = [
    path('result', views.game_results, name='game-result'),
    path('invites-recieved', views.received_invites, name='recieved-invites'),
    path('invite/<user_id>', views.send_game_invite, name='game-invite'),
    path('invite/accept/<invite_id>', views.game_invite_accept, name='game-invite-accept'),
]