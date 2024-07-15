from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from user.models import UserAccount
from django.conf import settings
from django.utils import timezone  
from notification.models import Notification
from django.db.models.signals import post_save
from django.dispatch import receiver                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          


class FriendRequest(models.Model):
    sender = models.ForeignKey(UserAccount, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(UserAccount, related_name='received_requests', on_delete=models.CASCADE)
    is_active = models.BooleanField(blank=True, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notifications = GenericRelation(Notification)

    def accept(self):
        receiver_list = FriendList.objects.get(user=self.receiver)
        if receiver_list:
            content_type = ContentType.objects.get_for_model(self)
			#Update notification for RECEIVER
            receiver_notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
            receiver_notification.is_active = False
            receiver_notification.read = True
            receiver_notification.redirect_url = f"profile/{self.sender.pk}"
            receiver_notification.description = f"You accepted {self.sender.username}'s friend request."
            receiver_notification.timestamp = timezone.now()
            receiver_notification.save()

            receiver_list.add_friend(self.sender)
            sender_list = FriendList.objects.get(user=self.sender)
            if sender_list:
                #Create notification for SENDER
                self.notifications.create(
					target=self.sender,
					from_user=self.receiver,
					redirect_url=f"profile/{self.receiver.pk}",
					description=f"{self.receiver.username} accepted your friend request.",
					content_type=content_type,
				)
                sender_list.add_friend(self.receiver)
                self.is_active = False
                self.save()
        return receiver_notification


    def reject(self):
        self.is_active = False
        self.save()

        content_type = ContentType.objects.get_for_model(self)
		#Update notification for RECEIVER
        notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
        notification.is_active = False
        notification.read = True
        notification.redirect_url = f"profile/{self.sender.pk}"
        notification.description = f"You declined {self.sender}'s friend request."
        notification.from_user = self.sender
        notification.timestamp = timezone.now()
        notification.save()
		#Create notification for SENDER
        self.notifications.create(
            target=self.sender,
            description=f"{self.receiver.username} declined your friend request.",
            from_user=self.receiver,
            redirect_url=f"profile/{self.receiver.pk}",
            content_type=content_type,
        )
        return notification

    def cancel(self):
        self.is_active = False
        self.save()

        content_type = ContentType.objects.get_for_model(self)
        # Create notification for SENDER
        self.notifications.create(
            target=self.sender,
            description=f"You cancelled the friend request to {self.receiver.username}.",
            from_user=self.receiver,
            redirect_url=f"profile/{self.receiver.pk}",
            content_type=content_type,
        )
        notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
        notification.description = f"{self.sender.username} cancelled the friend request."
        notification.read = False
        notification.save()

    @property
    def get_cname(self):
        return 'FriendRequest'


class FriendList(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    friends = models.ManyToManyField(UserAccount, blank=True, related_name='friends')
    notifications = GenericRelation(Notification)

    def __str__(self):
        return self.user.username
    
    def add_friend(self, account):
        if not account in self.friends.all():
            self.friends.add(account)
            self.save()

            content_type = ContentType.objects.get_for_model(self)
			# Notification(
			# 	target=self.user,
			# 	from_user=account,
			# 	redirect_url=f"profile/{account.pk}",
			# 	description=f"You are now friends with {account.username}.",
			# 	content_type=content_type,
			# 	object_id=self.id,
			# ).save()
            
            self.notifications.create(
				target=self.user,
				from_user=account,
				redirect_url=f"profile/{account.pk}",
				description=f"You are now friends with {account.username}.",
				content_type=content_type,
			)
            self.save()

    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account)
    
    def unfriend(self, friend):
        user = self
        user.remove_friend(friend)
        friendList = FriendList.objects.get(user=friend)
        friendList.remove_friend(self.user)

        content_type = ContentType.objects.get_for_model(self)

		# Create notification for removee
        self.notifications.create(
			target=friend,
			from_user=self.user,
			redirect_url=f"profile/{self.user.pk}",
			description=f"You are no longer friends with {self.user.username}.",
			content_type=content_type,
		)

		# Create notification for remover
        self.notifications.create(
			target=self.user,
			from_user=friend,
			redirect_url=f"profile/{friend.pk}",
			description=f"You are no longer friends with {friend.username}.",
			content_type=content_type,
		)
    
    def is_mutual_friend(self, friend):
        if friend in self.friends.all():
            return True
        return False
    
    @property
    def get_cname(self):
        return 'FriendList'


class BlockList(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    blocked = models.ManyToManyField(UserAccount, blank=True, related_name='blocked')

    def __str__(self):
        return self.user.username
    
    def block_user(self, account):
        if not account in self.blocked.all() and account != self.user:
            self.blocked.add(account)
            self.save()

    def unblock_user(self, account):
        if account in self.blocked.all() and account != self.user:
            self.blocked.remove(account)

    def is_blocked(self, account):
        if account in self.blocked.all():
            return True
        return False
    
    @staticmethod
    def is_either_blocked(auth_user, that_user):
        block_list = BlockList.objects.get(user=auth_user)
        other_block_list = BlockList.objects.get(user=that_user)

        if block_list and block_list.is_blocked(that_user) or other_block_list and other_block_list.is_blocked(auth_user):
            return True
        return False


@receiver(post_save, sender=FriendRequest)
def create_notification(sender, instance, created, **kwargs):
	if created:
		instance.notifications.create(
			target=instance.receiver,
			from_user=instance.sender,
			redirect_url=f"profile/{instance.sender.pk}",
			description=f"{instance.sender.username} sent you a friend request.",
			content_type=instance,
		)