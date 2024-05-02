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


class GameRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'invitee', 'is_active']
    list_search = ['user', 'invitee']
    list_filter = ['user', 'invitee', 'is_active']
    readonly_fields = ['user', 'invitee', 'is_active']

    class Meta:
        model = GameRequest

admin.site.register(GameRequest, GameRequestAdmin)


class GameScheduleAdmin(admin.ModelAdmin):
    list_display = ['player_one', 'player_two', 'is_active', 'scheduled', 'timestamp']

    class Meta:
        model = GameSchedule

admin.site.register(GameSchedule, GameScheduleAdmin)