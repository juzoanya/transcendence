from .models import *
from django.contrib.auth import get_user_model
from django.http import JsonResponse

def send_invite(user, invitee, game_id, game_mode, tournament):
    if invitee != user:
        try:
            request = GameRequest.objects.create(
            user=user, 
            invitee=invitee, 
            game_id=game_id, 
            game_mode=game_mode,
            tournament=tournament
            )
            request.save()
            return 'invitation was sent'
        except Exception as e:
            return str(e)
    

def tournament_details(tournament):
    players = []
    fixtures = []
    details = model_object_serializer(tournament)
    details['game_id'] = tournament.get_game_id_display()
    details['creator'] = Player.objects.get(user=tournament.creator).alias
    tournament_players = tournament.players.all()
    for player in tournament_players:
        player_details = UserAccount.objects.get(username=player)
        item = {
            'id': player_details.pk,
            'username': player_details.username,
            'avatar': player_details.avatar.url,
            'alias': player.alias
        }
        players.append(item)
    details['players'] = players
    schedules = GameSchedule.objects.filter(tournament=tournament, is_active=True)
    for schedule in schedules:
        ply_1 = UserAccount.objects.get(username=schedule.player_one)
        ply_2 = UserAccount.objects.get(username=schedule.player_two)
        item = {
            'id': schedule.id,
            'game_id': schedule.get_game_id_display(),
            'tournament': schedule.tournament.name,
            'player_one': {
                'id': ply_1.pk,
                'username': ply_1.username,
                'avatar': ply_1.avatar.url,
                'alias': schedule.player_one.alias
            },
            'player_two': {
                'id': ply_2.pk,
                'username': ply_2.username,
                'avatar': ply_2.avatar.url,
                'alias': schedule.player_two.alias
            }
        }
        fixtures.append(item)
    details['schedules'] = fixtures
    return details


def tournament_player_creator(user, tournament):
    try:
        tournament_player = TournamentPlayer.objects.create(player=Player.objects.get(user=user), tournament=tournament)
    except Exception as e:
        tournament.delete()
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
