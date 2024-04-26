from typing import Iterable
from django.db import models
from user.models import *
from user.utils import *

# Create your models here.

# deleted_user = UserAccount.objects.create_user(username='disabled', email='disabled@dis.dis', password='')

class GameResults(models.Model): #TODO: change on_delete to SET_DEFAULT and set user to disbaled user
    game_id = models.CharField(max_length=10, null=False)
    game_mode = models.CharField(max_length=20, null=False)
    player_one = models.ForeignKey(UserAccount, related_name='player_one', on_delete=models.SET_NULL, null=True)
    player_two = models.ForeignKey(UserAccount, related_name='player_two', on_delete=models.SET_NULL, null=True)
    player_one_score = models.IntegerField()
    player_two_score = models.IntegerField()
    winner = models.ForeignKey(UserAccount, related_name='winner', on_delete=models.SET_NULL, null=True)
    loser = models.ForeignKey(UserAccount, related_name='loser', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.winner or not self.loser:
            if self.player_one_score > self.player_two_score:
                self.winner = self.player_one
                self.loser = self.player_two
            elif self.player_two_score > self.player_one_score:
                self.winner = self.player_two
                self.loser = self.player_one
        super().save(*args, **kwargs)