import json
from django.db.models import Q
from django.conf import settings
from django.shortcuts import render, redirect
from user.models import *
from friends.models import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
@login_required
def game_results(request, *args, **kwargs):
	if request.method == 'POST':
		data = json.loads(request.body)
		game_id = data.get('game_id')
		game_mode = data.get('game_mode')
		player_one = data.get('player_one')
		player_two = data.get('player_two')
		score_one = data.get('score_one')
		score_two = data.get('score_two')

		if not player_one or not player_two:
			return JsonResponse({'success': False, 'message': 'Player field cannot be empty.'}, status=400)

		try:
			user_one = UserAccount.objects.get(username=Player.objects.get(alias=player_one))
			user_two = UserAccount.objects.get(username=Player.objects.get(alias=player_two))
		except Exception as e:
			return JsonResponse({'success': False, 'message': str(e)}, status=400)
		
		if user_one == user_two:
			return JsonResponse({'success': False, 'message': 'Player fields cannot be the same.'}, status=400)

		try:
			result = GameResults.objects.create(
				game_id=game_id,
				game_mode=game_mode,
				player_one=user_one,
				player_two=user_two,
				player_one_score=score_one,
				player_two_score=score_two
			)
			result.save()
		except Exception as e:
			return JsonResponse({'success': False, 'message': str(e)}, status=400)

		if result.winner and result.loser:
			try:
				winner_player = Player.objects.get(user=result.winner)
				winner_player.games_played = winner_player.games_played + 1
				winner_player.wins = winner_player.wins + 1
				winner_player.save()
			except Exception as e:
				return JsonResponse({'success': False, 'message': str(e)}, status=400)

			try:
				loser_player = Player.objects.get(user=result.loser)
				loser_player.games_played = loser_player.games_played + 1
				loser_player.losses = loser_player.losses + 1
				loser_player.save()
			except Exception as e:
				return JsonResponse({'success': False, 'message': str(e)}, status=400)
		else:
			return JsonResponse({'success': False, 'message': 'Internal server error'}, status=500)

		return JsonResponse({'success': True, 'message': 'record created'}, status=200)
	else:
		return JsonResponse({'success': False}, status=403)



@csrf_exempt
@login_required
def send_game_invite(request, *args, **kwargs):
	user = request.user
	user_id = kwargs.get('user_id')
	if request.method == 'POST':
		try:
			invitee = UserAccount.objects.get(pk=user_id)
		except Exception as e:
			return JsonResponse({'success': False, 'message': str(e)}, status=400)

		check_request = GameRequest.objects.get(user=user, invitee=invitee, is_active=True)
		if check_request:
			return JsonResponse({'success': False, 'message': 'Duplicate invite not permitted'}, status=400)

		if BlockList.is_either_blocked(user, invitee) == False:
			try:
				request = GameRequest.objects.create(user=user, invitee=invitee)
				request.save()
				return JsonResponse({'success': True, 'message': 'invitation was sent'}, status=200)
			except Exception as e:
				return JsonResponse({'success': False, 'message': str(e)}, status=400)
		else:
			return JsonResponse({'success': False, 'message': 'Blocklist: cannot invite user'}, status=400)
	else:
		return JsonResponse({'success': False}, status=403)


@csrf_exempt
@login_required
def received_invites(request, *args, **kwargs):
	user = request.user
	invites_recieved = []
	if request.method == 'POST':
		try:
			invites = GameRequest.objects.filter(invitee=user)
		except Exception as e:
			return JsonResponse({'success': False, 'message': str(e)}, status=400)
		
		for invite in invites:
			inviter = UserAccount.objects.get(username=invite.user)
			player = Player.objects.get(user=inviter)
			item = {
				'invite_id': invite.pk,
				'inviter': inviter.username,
				'alias': player.alias,
				'avatar': inviter.avatar.url,
			}
			invites_recieved.append(item)
		return JsonResponse({'data': invites_recieved})
	else:
		return JsonResponse({'success': False}, status=403)
	

@csrf_exempt
@login_required
def sent_invites(request, *args, **kwargs):
	user = request.user
	invites_sent= []
	if request.method == 'POST':
		try:
			invites = GameRequest.objects.filter(user=user)
		except Exception as e:
			return JsonResponse({'success': False, 'message': str(e)}, status=400)
		
		for invite in invites:
			invitee = UserAccount.objects.get(username=invite.invitee)
			player = Player.objects.get(user=invitee)
			item = {
				'invite_id': invite.pk,
				'invitee': invitee.username,
				'alias': player.alias,
				'avatar': invitee.avatar.url,
			}
			invites_sent.append(item)
		return JsonResponse({'data': invites_sent})
	else:
		return JsonResponse({'success': False}, status=403)

@csrf_exempt
@login_required
def game_invite_accept(request, *args, **kwargs):
	user = request.user
	if request.method == 'POST':
		invite_id = kwargs.get('invite_id')
		data = json.loads(request.body)
		alias = data.get('display_name')
		if invite_id:
			game_invite = GameRequest.objects.get(pk=invite_id)
			if game_invite:
				if game_invite.invitee == user:
					game_invite.accept()
					try:
						player = Player.objects.get(user=user)
						player.alias = alias
						player.save()
					except Exception as e:
						return JsonResponse({'success': False, 'message': str(e)}, status=400)
					return JsonResponse({'success': True, 'message': 'Invite accepted.'}, status=200)
				else:
					return JsonResponse({'success': False, 'message': 'You cannot access this feature'}, status=400)
			else:
				return JsonResponse({'success': False, 'message': 'This invite does not exist'}, status=400)
		else:
			return JsonResponse({'success': False, 'message': 'Invite is invalid.'}, status=400)
	else:
		return JsonResponse({'success': False}, status=403)



@csrf_exempt
@login_required
def game_invite_reject(request, *args, **kwargs):
	user = request.user
	if request.method == 'POST':
		invite_id = kwargs.get('invite_id')
		if invite_id:
			game_invite = GameRequest.objects.get(pk=invite_id)
			if game_invite:
				if game_invite.user == user:
					game_invite.reject()
					return JsonResponse({'success': True, 'message': 'Invite rejected.'}, status=200)
				else:
					return JsonResponse({'success': False, 'message': 'You cannot access this feature'}, status=400)
			else:
				return JsonResponse({'success': False, 'message': 'This invite does not exist'}, status=400)
		else:
			return JsonResponse({'success': False, 'message': 'Invite is invalid.'}, status=400)
	else:
		return JsonResponse({'success': False}, status=403)


@csrf_exempt
@login_required
def game_invite_cancel(request, *args, **kwargs):
	pass


@csrf_exempt
@login_required
def create_tournament(request, *args, **kwargs):
	pass



@csrf_exempt
@login_required
def game_schedule(request, *args, **kwargs):
	user = request.user
	schedules = []
	if request.method == 'POST':
		player = Player.objects.get(user=user)
		if player:
			try:
				game_list = GameSchedule.objects.filter(Q(player_one=player) | Q(player_two=player), is_active=True)
			except Exception as e:
				return JsonResponse({'success': False, 'message': str(e)}, status=400)
		else:
			return JsonResponse({'success': False, 'message': 'Player does not exist'}, status=400)

		for game in game_list:
			ply_one_user_acc = UserAccount.objects.get(username=game.player_one)
			ply_two_user_acc = UserAccount.objects.get(username=game.player_two)
			item = {
				'schedule_id': game.pk,
				'player_one': {
					'id': ply_one_user_acc.pk,
					'username': ply_one_user_acc.username,
					'avatar': ply_one_user_acc.avatar.url,
					'alias': Player.objects.get(user=ply_one_user_acc).alias,
				},
				'player_two': {
					'id': ply_two_user_acc.pk,
					'username': ply_two_user_acc.username,
					'avatar': ply_two_user_acc.avatar.url,
					'alias': Player.objects.get(user=ply_two_user_acc).alias,
				}
			}
			schedules.append(item)
		return JsonResponse({'data': schedules}, status=200)
	else:
		return JsonResponse({'success': False}, status=403)


@csrf_exempt
@login_required
def match_history(request, *args, **kwargs):
	user = request.user
	history = []
	if request.method == 'GET':
		player = UserAccount.objects.get(username=user)
		if player:
			try:
				games_played = GameResults.objects.filter(Q(player_one=player) | Q(player_two=player))
			except Exception as e:
				return JsonResponse({'success': False, 'message': str(e)}, status=400)
		else:
			return JsonResponse({'success': False, 'message': 'Player does not exist'}, status=400)

		for game in games_played:
			ply_one_user_acc = UserAccount.objects.get(username=game.player_one)
			ply_two_user_acc = UserAccount.objects.get(username=game.player_two)
			item = {
				'match_id': game.pk,
				'game_id': game.game_id,
				'game_mode': game.game_mode,
				'player_one': {
					'id': ply_one_user_acc.pk,
					'username': ply_one_user_acc.username,
					'avatar': ply_one_user_acc.avatar.url,
					'alias': Player.objects.get(user=ply_one_user_acc).alias,
				},
				'player_two': {
					'id': ply_two_user_acc.pk,
					'username': ply_two_user_acc.username,
					'avatar': ply_two_user_acc.avatar.url,
					'alias': Player.objects.get(user=ply_two_user_acc).alias
				},
				'player_one_score': game.player_one_score,
				'player_two_score': game.player_two_score,
				'winner': Player.objects.get(user=game.winner).alias
				# 'winner': game.winner.username
			}
			history.append(item)
		return JsonResponse({'data': history}, status=200)
	else:
		return JsonResponse({'success': False}, status=403)
