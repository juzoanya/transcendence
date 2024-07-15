import json
from django.conf import settings
from datetime import datetime
from user.models import UserAccount
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.paginator import Paginator
from django.core.serializers import serialize
from channels.db import database_sync_to_async
from django.contrib.contenttypes.models import ContentType
from friends.models import FriendRequest, FriendList
from game.models import GameRequest
from notification.utils import LazyNotificationEncoder
from django.contrib.auth.decorators import login_required
from notification.constants import *
from notification.models import Notification



class NotificationConsumer(AsyncJsonWebsocketConsumer):

	async def connect(self):
		print("NotificationConsumer: connect: " + str(self.scope["user"]) )
		await self.accept()


	async def disconnect(self, code):
		print("NotificationConsumer: disconnect")

	#Fix errors
	async def receive_json(self, content):
		command = content.get("command", None)
		print("NotificationConsumer: receive_json. Command: " + command)
		try:
			user_account = self.scope['user']
			if command == "get_general_notifications":
				data = await get_general_notifications(user_account, content.get('page_number', None))
				if data == None:
					pass
				else:
					data = json.loads(data)
					await self.send_general_notifications_data(data['notifications'], data['new_page_number'])
			elif command == "accept_friend_request":
				notification_id = content['notification_id']
				data = await accept_friend_request(user_account, notification_id)
				if data == None:
					raise ("Something went wrong. Try refreshing the browser.") #TODO:
				else:
					data = json.loads(data)
					await self.send_updated_friend_request_notification(data['notification'])
			elif command == "reject_friend_request":
				notification_id = content['notification_id']
				data = await reject_friend_request(user_account, notification_id)
				if data == None:
					raise ("Something went wrong. Try refreshing the browser.") #TODO:
				else:
					data = json.loads(data)
					await self.send_updated_friend_request_notification(data['notification'])
			elif command == "refresh_general_notifications":
				print(f'@@@---->Oldest = {content['oldest_timestamp']} || -->Newsest = {content['newest_timestamp']}')
				data = await refresh_general_notifications(user_account, content['oldest_timestamp'], content['newest_timestamp'])
				if data == None:
					raise ("Something went wrong. Try refreshing the browser.") #TODO:
				else:
					data = json.loads(data)
					await self.send_general_refreshed_notifications_data(data['notifications'])
		except Exception as e:
			print("\nEXCEPTION: receive_json: " + str(e) + '\n') #TODO:
			pass

	async def send_general_notifications_data(self, notifications, new_page_number):
		await self.send_json(
			{
				"general_msg_type": GENERAL_MSG_TYPE_NOTIFICATIONS_DATA,
				"notifications": notifications,
				"new_page_number": new_page_number,
			},
		)
	
	async def send_updated_friend_request_notification(self, notification):
		"""
		After a friend request is accepted or rejected, send the updated notification to template
		data contains 'notification' and 'response':
		1. data['notification']
		2. data['response']
		"""
		await self.send_json(
			{
				"general_msg_type": GENERAL_MSG_TYPE_UPDATED_NOTIFICATION,
				"notification": notification,
			},
		)

	async def general_pagination_exhausted(self):
		"""
		Called by receive_json when pagination is exhausted for general notifications
		"""
		#print("General Pagination DONE... No more notifications.")
		await self.send_json(
			{
				"general_msg_type": GENERAL_MSG_TYPE_PAGINATION_EXHAUSTED,
			},
		)
	
	async def display_progress_bar(self, shouldDisplay):
		print("NotificationConsumer: display_progress_bar: " + str(shouldDisplay)) 
		await self.send_json(
			{
				"progress_bar": shouldDisplay,
			},
		)
	
	async def send_general_refreshed_notifications_data(self, notifications):
		"""
		Called by receive_json when ready to send a json array of the notifications
		"""
		#print("NotificationConsumer: send_general_refreshed_notifications_payload: " + str(notifications))
		await self.send_json(
			{
				"general_msg_type": GENERAL_MSG_TYPE_NOTIFICATIONS_REFRESH_PAYLOAD,
				"notifications": notifications,
			},
		)

@database_sync_to_async
def get_general_notifications(user, page_number):
	"""
	Get General Notifications with Pagination (next page of results).
	This is for appending to the bottom of the notifications list.
	"""
	if user.is_authenticated:
		friend_request_ct = ContentType.objects.get_for_model(FriendRequest)
		friend_list_ct = ContentType.objects.get_for_model(FriendList)
		game_request_ct = ContentType.objects.get_for_model(GameRequest)
		notifications = Notification.objects.filter(
			target=UserAccount.objects.get(username=user),
			content_type__in=[friend_request_ct, friend_list_ct, game_request_ct]
		).order_by('-timestamp')
		pages = Paginator(notifications, DEFAULT_NOTIFICATION_PAGE_SIZE)
		data = {}
		if len(notifications) > 0:
			print(f'length = {len(notifications)}')
			if int(page_number) <= pages.num_pages:
				item = LazyNotificationEncoder()
				serialized_notifications = item.serialize(pages.page(page_number).object_list)
				data['notifications'] = serialized_notifications
				new_page_number = int(page_number) + 1
				data['new_page_number'] = new_page_number
		else:
			return None
		return json.dumps(data)
	return None


@database_sync_to_async
def accept_friend_request(user, notification_id):
    """
    Accept a friend request from within the notification
    """
    data = {}
    if user.is_authenticated:
        try:
            notification = Notification.objects.get(pk=notification_id)
            friend_request = notification.content_object
            if friend_request.receiver == user:
                updated_notification = friend_request.accept()
                item = LazyNotificationEncoder()
                data['notification'] = item.serialize([updated_notification])[0]
                return json.dumps(data)
        except Notification.DoesNotExist:
            raise ("An error occurred with that notification. Try refreshing the browser.") #TODO:
    return None


@database_sync_to_async
def reject_friend_request(user, notification_id):
    """
    Dccept a friend request from within the notification
    """
    data = {}
    if user.is_authenticated:
        try:
            notification = Notification.objects.get(pk=notification_id)
            friend_request = notification.content_object
            if friend_request.receiver == user:
                updated_notification = friend_request.reject()
                item = LazyNotificationEncoder()
                data['notification'] = item.serialize([updated_notification])[0]
                return json.dumps(data)
        except Notification.DoesNotExist:
            raise ("An error occurred with that notification. Try refreshing the browser.") #TODO:
    return None

@database_sync_to_async
def refresh_general_notifications(user, oldest_timestamp, newest_timestamp):
	"""
	Retrieve the general notifications newer than the oldest one on the screen and younger than the newest one the screen.
	The result will be: Notifications currently visible will be updated
	"""
	data = {}
	if user.is_authenticated:
		friend_request_ct = ContentType.objects.get_for_model(FriendRequest)
		print('Start---> 000 <<<<<<<<<<<<')
		friend_list_ct = ContentType.objects.get_for_model(FriendList)
		game_request_ct = ContentType.objects.get_for_model(GameRequest)
		print('Start---> 111 <<<<<<<<<<<<')
		notifications = Notification.objects.filter(
			target=user, content_type__in=[friend_request_ct, friend_list_ct, game_request_ct], read=False).order_by('-timestamp')
		# 	timestamp__gte=oldest_ts,
		# 	timestamp__lte=newest_ts
		# ).order_by('-timestamp')
		print('Start---> 222 <<<<<<<<<<<<')
		item = LazyNotificationEncoder()
		print('Start---> ==+== <<<<<<<<<<<<')
		data['notifications'] = item.serialize(notifications)
	else:
		raise ("User must be authenticated to get notifications.") #TODO:

	return json.dumps(data) 