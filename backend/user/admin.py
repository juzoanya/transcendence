from django.contrib import admin
from .models import Profile, Player, Tournament, TournamentInvite, TournamentLobby, GameSession, MatchHistory

# Register your models here.

admin.site.register(Profile)
admin.site.register(Player)