from django.db import models
from user.models import UserAccount
from django.conf import settings


class ChatRoom(models.Model):
	title = models.CharField(max_length=255, unique=True, blank=False,)
	type = models.CharField(max_length=30, blank=False)
	is_active = models.BooleanField(default=True)
	users = models.ManyToManyField(settings.AUTH_USER_MODEL, help_text="users who are connected to chat room.", blank=True, null=True)

	def __str__(self):
		return self.title
	

	def connect_user(self, user):
		is_user_added = False
		if not user in self.users.all():
			self.users.add(user)
			self.save()
			is_user_added = True
		elif user in self.users.all():
			is_user_added = True
		return is_user_added 


	def disconnect_user(self, user):
		is_user_removed = False
		if user in self.users.all():
			self.users.remove(user)
			self.save()
			is_user_removed = True
		return is_user_removed 


	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent messages as they are generated."""
		return f'{self.type}-chatroom-{self.id}'


class ChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = ChatMessage.objects.filter(room=room).order_by("-timestamp")
        return qs


class ChatMessage(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(unique=False, blank=False,)

    objects = ChatMessageManager()

    def __str__(self):
        return self.content
