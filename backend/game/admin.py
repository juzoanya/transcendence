from django.contrib import admin
from .models import *

# Register your models here.

class GameResultAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'game_mode', 'player_one', 'player_two', 'player_one_score', 'player_two_score', 'winner', 'timestamp']
    list_search = ['game_id', 'game_mode', 'player_one', 'player_two']
    list_filter = ['game_id', 'game_mode', 'player_one', 'player_two']
    readonly_fields = ['game_id', 'game_mode', 'player_one', 'player_two', 'player_one_score', 'player_two_score', 'winner', 'loser', 'timestamp']

    class Meta:
        model = GameResults

admin.site.register(GameResults, GameResultAdmin)