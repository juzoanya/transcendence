from django.shortcuts import render


# Create your views here.

def remote_game(request, *args, **kwargs):
    return render(request, 'game/game.html')