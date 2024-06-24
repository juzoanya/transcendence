from typing import Iterable
from django.db import models
from user.models import *
from user.utils import *
from django.db.models import Max



class Tournament(models.Model):
	class GameID(models.IntegerChoices):
		Pong = 0, 'Pong'
		Other = 1, 'Other'
	name = models.CharField(max_length=30, default='Tournament')
	game_id = models.IntegerField(choices=GameID.choices, null=True)
	mode = models.CharField(max_length=50, blank=False)
	creator = models.ForeignKey(UserAccount, related_name='tournament_creator', on_delete=models.CASCADE)
	players = models.ManyToManyField(Player, related_name='tournament_players')
	nb_player = models.IntegerField(null=True, blank=True)
	nb_rounds = models.IntegerField(null=True, blank=True)
	status = models.CharField(max_length=20, default='waiting')
	stage = models.CharField(max_length=20, null=True, blank=True)
	started = models.DateTimeField(null=True, blank=True)
	ended = models.DateTimeField(null=True, blank=True)
	winner = models.ForeignKey(UserAccount, related_name='tournament_winner', on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return self.name
	
	def update(self):
		pass
	
	def matchmaking(self):
		tournament_players = TournamentPlayer.objects.filter(tournament=self)
		max_round = tournament_players.aggregate(Max('num_round'))['num_round__max']
		players = list(tournament_players.filter(num_round=max_round))
		if self.status != 'finished':
			mode = self.mode
			if mode == 'round robin':
				self.round_robin(players)
			elif mode == 'single elimination':
				self.single_elimination(players)
			elif mode == 'double elimination':
				self.double_elimination(players)
	
	def round_robin(self, players):
		pass

	def single_elimination(self, players):
		if len(players) > 1:
			for i in range(0, len(players) // 2):
				schedule = GameSchedule.objects.create(
					game_id=self.game_id,
					game_mode='tournament',
					tournament=self,
					player_one=players[i].player,
					player_two=players[-(i + 1)].player
				)

	def double_elimination(self, players):
		pass



class TournamentPlayer(models.Model):
	tournament = models.ForeignKey(Tournament, related_name='tournament_players', on_delete=models.CASCADE)
	player = models.ForeignKey(Player, related_name='player_tournaments', on_delete=models.CASCADE)
	xp = models.IntegerField(default=0)
	num_round = models.IntegerField(default=0)
	round = models.CharField(max_length=30, default='First Round')



class TournamentLobby(models.Model):
	tournament = models.ForeignKey(Tournament, related_name='tournament_tl', on_delete=models.CASCADE)
	winners = models.ManyToManyField(Player, related_name='winners')
	losers = models.ManyToManyField(Player, related_name='losers')


class GameResults(models.Model):
	game_id = models.CharField(max_length=10, null=False)
	game_mode = models.CharField(max_length=20, null=False)
	tournament = models.ForeignKey(Tournament, related_name='tournament_name', on_delete=models.SET_NULL, null=True, blank=True)
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


class GameSchedule(models.Model):
	class GameID(models.IntegerChoices):
		Pong = 0, 'Pong'
		Other = 1, 'Other'
	game_id = models.IntegerField(choices=GameID.choices, null=True)
	game_mode = models.CharField(max_length=20, null=True)
	tournament = models.ForeignKey(Tournament, related_name='tournament_gs', on_delete=models.SET_NULL, null=True, blank=True)
	player_one = models.ForeignKey(Player, related_name='player_one', on_delete=models.CASCADE)
	player_two = models.ForeignKey(Player, related_name='player_two', on_delete=models.CASCADE)
	is_active = models.BooleanField(blank=True, null=False, default=True)
	scheduled = models.DateTimeField(blank=True, null=True)
	timestamp = models.DateTimeField(auto_now_add=True)


class GameRequest(models.Model):

	class GameID(models.IntegerChoices):
		Pong = 0, 'Pong'
		Other = 1, 'Other'
	game_id = models.IntegerField(choices=GameID.choices, null=True)
	game_mode = models.CharField(max_length=20, null=True)
	tournament = models.ForeignKey(Tournament, related_name='tournament_gr', on_delete=models.SET_NULL, null=True, blank=True)
	user = models.ForeignKey(UserAccount, related_name='inviter', on_delete=models.CASCADE)
	invitee = models.ForeignKey(UserAccount, related_name='invitee', on_delete=models.CASCADE)
	is_active = models.BooleanField(blank=True, null=False, default=True)
	status = models.CharField(max_length=20, default='pending')
	timestamp = models.DateTimeField(auto_now_add=True)

	def accept(self):
		player_one = Player.objects.get(user=self.user)
		player_two = Player.objects.get(user=self.invitee)
		if self.game_mode == 'tournament' and self.tournament != None:
			TournamentPlayer.objects.create(tournament=self.tournament, player=Player.objects.get(user=self.invitee) )
			if len(TournamentPlayer.objects.filter(tournament=self.tournament)) == len(self.tournament.players.all()):
				self.tournament.matchmaking()
		else:
			game = GameSchedule.objects.create(
				player_one=player_one,
				player_two=player_two,
				game_id=self.game_id,
				game_mode=self.game_mode,
				tournament=self.tournament
			)
			game.save()
		self.is_active = False
		self.status = 'accepted'
		self.save()

	def reject(self):
		self.is_active = False
		self.status = 'rejected'
		if self.game_mode == 'tournament' and self.tournament != None:
			user = UserAccount.objects.get(username=self.invitee)
			self.tournament.players.remove(Player.objects.get(user=user))
			if len(TournamentPlayer.objects.filter(tournament=self.tournament)) == len(self.tournament.players.all()):
				self.tournament.matchmaking()
		self.save()

	def cancel(self):
		self.is_active = False
		self.status = 'cancelled'
		if self.game_mode == 'tournament' and self.tournament != None:
			user = UserAccount.objects.get(username=self.invitee)
			self.tournament.players.remove(Player.objects.get(user=user))
			if len(TournamentPlayer.objects.filter(tournament=self.tournament)) == len(self.tournament.players.all()):
				self.tournament.matchmaking()
		self.save()





