import json
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

        user_one = UserAccount.objects.get(username=Player.objects.get(alias=player_one))
        user_two = UserAccount.objects.get(username=Player.objects.get(alias=player_two))

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
            return JsonResponse({'success': True, 'message': 'record created'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    else:
        return JsonResponse({'success': False}, status=403)


@csrf_exempt
@login_required
def match_history(request, *args, **kwargs):
    pass


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
        
        try:
            request = GameRequest.objects.create(user=user, invitee=invitee)
            request.save()
            return JsonResponse({'success': True, 'message': 'invitation was sent'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
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
            player = Player.objects.get(user=inviter.user)
            item = {
                'invite_id': invite.pk,
                'inviter': inviter.username,
                'alias': player.alias,
                'avatar': inviter.avatar.url,

            }
            invites_recieved.append(item)
        return JsonResponse({'invites': invites_recieved})
    else:
        return JsonResponse({'success': False}, status=403)
    

@csrf_exempt
@login_required
def sent_invites(request, *args, **kwargs):
    pass

@csrf_exempt
@login_required
def game_invite_accept(request, *args, **kwargs):
    pass



@csrf_exempt
@login_required
def game_invite_reject(request, *args, **kwargs):
    pass


@csrf_exempt
@login_required
def game_invite_cancel(request, *args, **kwargs):
    pass


@csrf_exempt
@login_required
def create_tournament(request, *args, **kwargs):
    pass
