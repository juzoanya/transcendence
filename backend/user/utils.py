from .models import *
from django.contrib.auth import get_user_model
from django.http import JsonResponse


def set_default_avatar():
    return 'avatars/default_avatar.png'


def get_avatar_path(self, filename):
    return f"avatars/{self.pk}/{'avatar.png'}"

def get_default_user():
    return get_user_model().objects.get(username='root')


def model_object_serializer(object):
    data = {}
    for field in object._meta.fields:
        field_value = getattr(object, field.name)
        if hasattr(field_value, 'serialize'):
            field_value = field_value.serialize()
        elif hasattr(field_value, 'pk'):
            field_value = field_value.pk
        data[field.name] = field_value
    return data

def calculate_user_xp(margin, winner):
    xp_map = {
        range(1, 4): 1,
        range(4, 7): 2,
        range(7, 10): 3
    }
    xp = 0
    for margin_range, xp_value in xp_map.items():
        if margin in margin_range:
            xp = xp_value if winner else -xp_value
    return xp

def get_minimal_user_details(user):
    pass

def get_nth_string(num):
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
    return str(num) + suffix

def serializer_minimal_account_details(account):
    data = {
        'id': account.pk,
        'username': account.username,
        'email': account.email,
        'first_name': account.first_name,
        'last_name': account.last_name,
        'avatar': account.avatar.url
    }
    return data

def serializer_full_profile_details(account, player):
    data = {
        'id': account.pk,
        'username': account.username,
        'email': account.email,
        'first_name': account.first_name,
        'last_name': account.last_name,
        'avatar': account.avatar.url,
        'last_login': account.last_login,
        'date_joined': account.date_joined,
        'alias': player.alias,
        'games_played': player.games_played,
        'wins': player.wins,
        'losses': player.losses
    }
    return data

def serializer_inviter_invitee_details(invite, account, player, inviter):
    data = {
        'invite_id': invite.pk,
        'game_id': invite.game_id,
        'game_mode': invite.game_mode,
        'tournament': invite.tournament,
        'id': account.pk,
        'alias': player.alias,
        'avatar': account.avatar.url,
	}
    if inviter:
        data['inviter'] = account.username
    else:
        data['invitee'] = account.username
    return data

def serialize_player_details(account, player_object):
    print(f'---> Start')
    data = {
        'id': account.pk,
        'username': account.username,
        'avatar': account.avatar.url,
        'alias': player_object.alias,
    }
    print(f'--------> Done')
    return data


class Response(JsonResponse):
    def __init__(self, message: str,  data = None, success: bool = True, status: int = 200, safe: bool = True, **kwargs):
        super().__init__(data={'message': message, 'success': success, 'data': data},
        safe=safe, status=status, **kwargs
        )
class Success200(Response):
    def __init__(self, message: str, data = None):
        super().__init__(message=message, data=data, success=True, status=200)
class Created201(Response):
    def __init__(self, message: str, data = None):
        super().__init__(message=message, data=data, success=True, status=201)
class BadRequest400(Response):
    def __init__(self, message: str):
        super().__init__(message=message, success=False, status=400)
class NotAuthenticated401(Response):
    def __init__(self, message: str):
        super().__init__(message=message, success=False, status=401)
class Forbidden403(Response):
    def __init__(self, message: str):
        super().__init__(message=message, success=False, status=403)
class NotFound404(Response):
    def __init__(self, message: str):
        super().__init__(message=message, success=False, status=404)
class Conflict409(Response):
    def __init__(self, message: str):
        super().__init__(message=message, success=False, status=409)
class InternalServerError500(Response):
    def __init__(self, message: str):
        super().__init__(message=message, success=False, status=500)   