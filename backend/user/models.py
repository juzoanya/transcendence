from django.db import models
from django.contrib.auth.models import User, AbstractUser


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default_avatar.png')
    status = models.CharField(max_length=20, default='Offline')
    

class Player(models.Model):

    def get_default_value(self):
        return self.user.username
    
    user = models.OneToOneField(User, related_name='player', on_delete=models.CASCADE)
    display_name = models.CharField(max_length=30, default='get_default_value')
    games_played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)



class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    is_active = models.BooleanField(blank=True, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def accept(self):
        FriendList.objects.create(user=self.sender, friend=self.reciever)
        self.status = 'accepted'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()


class FriendList(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, blank=True, related_name='friends')

    def __str__(self):
        return self.user.username
    
    def add_friend(self, account):
        if not account in self.friends.all():
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account)
    
    def unfriend(self, friend):
        user = self
        user.remove_friend(friend)
        friendList = FriendList.objects.get(user=friend)
        friendList.remove_friend(self.user)
    
    def is_mutual_friend(self, friend):
        if friend in self.friends.all():
            return True
        return False



class GameSession(models.Model):
    class GameID(models.IntegerChoices):
        Pong = 0, 'Pong'
        Other = 1, 'Other'
    players = models.ManyToManyField(Player)
    player_scores = models.JSONField(default=dict)
    game_mode = models.CharField(max_length=20)
    game_id = models.IntegerField(choices=GameID.choices, null=True)


    def update_score(self, player, score):
        self.player_scores[player.username] = score
        self.save()

    def end_game(self):
        player_one = self.players.first()
        player_two = self.players.last()
        player_one_score = self.player_scores.get(player_one.username, 0)
        player_two_score = self.player_scores.get(player_two.username, 0)

        match_history = MatchHistory.objects.create(
            player_one = player_one,
            player_two = player_two,
            player_one_score = player_one_score,
            player_two_score = player_two_score,
            game_mode = self.game_mode,
            game_id = self.game_id
        )

        if player_one_score > player_two_score:
            winner = player_one
            losser = player_two
        else:
            winner = player_two
            losser = player_one
        
        # TODO: update the wins and losses in the user profile


class MatchHistory(models.Model):
    match_id = models.AutoField(primary_key=True)
    game_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    game_mode = models.CharField(max_length=20)
    player_one = models.ForeignKey(User, related_name='matches_as_player_one', on_delete=models.CASCADE)
    player_two = models.ForeignKey(User, related_name='matches_as_player_two', on_delete=models.CASCADE)
    player_one_score = models.PositiveIntegerField()
    player_two_score = models.PositiveIntegerField()
    result = models.CharField(max_length=50)

    # custom save fuction for the model to capture the resut field?
    def save(self, *args, **kwargs):
        pass


class Tournament(models.Model):
    class GameID(models.IntegerChoices):
        Pong = 0, 'Pong'
        Other = 1, 'Other'
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, default='Tournament')
    game_id = models.IntegerField(choices=GameID.choices, null=True)
    creator = models.ForeignKey(User, related_name='tournament_creator', on_delete=models.CASCADE)
    players = models.ManyToManyField(Player)
    nb_player = models.IntegerField(default=4)
    nb_rounds = models.IntegerField(default=2)
    status = models.CharField(max_length=20, default='waiting')
    started = models.DateTimeField(null=True, blank=True)
    ended = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, related_name='tournament_winner', on_delete=models.CASCADE)


class TournamentInvite(models.Model):
    id = models.AutoField(primary_key=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='invite_sent', on_delete=models.CASCADE)
    reciever = models.ForeignKey(User, related_name='invite_recieved', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)


class TournamentLobby(models.Model):
    id = models.AutoField(primary_key=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player_one = models.ForeignKey(User, related_name='tournament_as_player_one', on_delete=models.CASCADE)
    player_two = models.ForeignKey(User, related_name='tournament_as_player_two', on_delete=models.CASCADE)
    round = models.CharField(max_length=30, default='First Round')
    status = models.CharField(max_length=20, default='not started')
    result = models.CharField(max_length=50)



class Chat(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

