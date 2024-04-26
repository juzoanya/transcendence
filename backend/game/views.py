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
            return JsonResponse({'success': True, 'message': 'record created'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    else:
        return JsonResponse({'success': False}, status=403)
