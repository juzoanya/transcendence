from .models import *
from django.contrib.auth import get_user_model


def set_default_avatar():
    return 'avatars/default_avatar.png'


def get_avatar_path(self, filename):
    return f"avatars/{self.pk}/{'avatar.png'}"

def get_default_user():
    return get_user_model().objects.get(username='root')