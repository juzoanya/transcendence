from django.db import models
from user.models import UserAccount
from django.conf import settings                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 

# Create your models here.

class FriendRequest(models.Model):
    sender = models.ForeignKey(UserAccount, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(UserAccount, related_name='received_requests', on_delete=models.CASCADE)
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
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    friends = models.ManyToManyField(UserAccount, blank=True, related_name='friends')

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
