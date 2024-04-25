import json
from django.shortcuts import render
from .models import FriendList, FriendRequest
from user.models import UserAccount
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder



@login_required
def friend_list(request, *args, **kwargs):
	user = request.user
	user_id = kwargs.get('user-id')
	if user_id:
		try:
			this_user = UserAccount.objects.get(pk=user_id)
		except UserAccount.DoesNotExist:
			return JsonResponse({})
		try:
			friend_list = FriendList.objects.get(user=this_user)
		except FriendList.DoesNotExist:
			return JsonResponse({})
		
		if user != this_user:
			if not user in friend_list.friends.all():
				return JsonResponse({})
		
		friends = []
		user_friend_list = FriendList.objects.get(user=user)
		for friend in friend_list.firends.all():
			friends.append((friend, user_friend_list.is_mutual_friend(friend)))
		
		return JsonResponse({'data': friends}, status=200)
	else:
		return JsonResponse({'success': False}, status=400)



@login_required
def accept_friend_request(request, *args, **kwargs):
	user = request.user
	if request.method == 'GET':
		friend_request_id = kwargs.get('friend_request_id')
		if friend_request_id:
			friend_request = FriendRequest.objects.get(pk=friend_requests_sent)
			if friend_request:
				if friend_request.receiver == user:
					friend_request.accept()
					return JsonResponse({'success': True, 'message': 'Friend request accepted.'}, status=200)
				else:
					return JsonResponse({'success': False, 'message': 'You cannot access this feature'}, status=400)
			else:
				return JsonResponse({'success': False, 'message': 'This request does not exist'}, status=400)
		else:
			return JsonResponse({'success': False, 'message': 'Friend request is invalid.'}, status=400)
	else:
		return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
		


@login_required
def reject_friend_request(request, *args, **kwargs):
	user = request.user
	if request.method == 'GET':
		friend_request_id = kwargs.get('friend_request_id')
		if friend_request_id:
			friend_request = FriendList.objects.get(pk=friend_request_id)
			if friend_request:
				if friend_request.receiver == user:
					friend_request.reject()
					return JsonResponse({'success': True, 'message': 'Friend request rejected.'}, status=200)
				else:
					return JsonResponse({'success': False, 'message': 'You cannot access this feature'}, status=400)
			else:
				return JsonResponse({'success': False, 'message': 'This request does not exist'}, status=400)
		else:
			return JsonResponse({'success': False, 'message': 'Friend request is invalid.'}, status=400)
	else:
		return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)



@login_required
def cancel_friend_request(request, *args, **kwargs):
	user = request.user
	if request.method == 'POST':
		receiver_id = request.POST.get('receiver_id')
		if receiver_id:
			receiver = UserAccount.objects.get(pk=receiver_id)
			try:
				friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver, is_active=True)
			except Exception as e:
				return JsonResponse({'success': False, 'message': 'This request does not exist'}, status=400)
			if len(friend_requests) > 1:
				for request in friend_requests:
					request.cancel()
				return JsonResponse({'success': True, 'message': 'Friend request cancelled.'}, status=200)
			else:
				friend_requests.first().cancel()
				return JsonResponse({'success': True, 'message': 'Friend request cancelled.'}, status=200)
		else:
			return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
	else:
		return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)



@login_required
def friend_requests_sent(request, *args, **kwargs):
	user = request.user
	user_id = kwargs.get('user_id')
	account = UserAccount.objects.get(pk=user_id)
	data = []
	if account == user:
		sent_requests = FriendRequest.objects.filter(sender=account, is_active=True)
		for req in sent_requests:
			item = {
				'id': req.pk,
				'receiver': req.receiver.username,
				'avatar': req.receiver.avatar.url
			}
			data.append(item)
	else:
		return JsonResponse({'success': False, 'message': 'You cannot access this page'}, status=400)
	return JsonResponse({'data': data})



@login_required
def friend_requests_received(request, *args, **kwargs):
	user = request.user
	user_id = kwargs.get('user_id')
	account = UserAccount.objects.get(pk=user_id)
	data = []
	if account == user:
		friend_requests = FriendRequest.objects.filter(receiver=account, is_active=True)
		for req in friend_requests:
			item = {
				'id': req.pk,
				'sender':req.sender.username,
				'avatar': req.sender.avatar.url
			}
			data.append(item)
	else:
		return JsonResponse({'success': False, 'message': 'You cannot access this page'}, status=400)
	return JsonResponse({'data': data})



@login_required
def send_friend_request(request, *args, **kwargs):
	user = request.user
	if request.method == 'POST':
		data = json.loads(request.body)
		friend_id = data.get('receiver_id')
		if friend_id:
			receiver = UserAccount.objects.get(pk=friend_id)
			try:
				friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver)
				try:
					for req in friend_requests:
						if req.is_active:
							raise Exception("You have an active friend request.")
					friend_request = FriendRequest(sender=user, receiver=receiver)
					friend_request.save()
					return JsonResponse({'success': True, 'message': 'Friend request was sent'}, status=200)
				except Exception as e:
					return JsonResponse({'success': False, 'message': str(e)}, status=400)
			except FriendRequest.DoesNotExist:
				friend_request = FriendRequest(sender=user, receiver=receiver)
				friend_request.save()
				return JsonResponse({'success': True, 'message': 'Friend request was sent'}, status=200)
		else:
			return JsonResponse({'success': False, 'message': 'User does not exist'}, status=404)
	else:
		return JsonResponse({'success': False, 'message': 'method not allowed'}, status=403)
	


@login_required
def remove_friend(request, *args, **kwargs):
	user = request.user
	if request.method == 'POST':
		data = json.loads(request.body)
		user_id = data.get('receiver_id')
		if user_id:
			try:
				to_remove = UserAccount.objects.get(pk=user_id)
				remover_friend_list = FriendList.objects.get(user=user)
				remover_friend_list.unfriend(to_remove)
				return JsonResponse({'success': True, 'message': 'Friend request removed.'}, status=200)
			except Exception as e:
				return JsonResponse({'success': False, 'message': str(e)}, status=400)
		else:
			return JsonResponse({'success': False, 'message': 'Bad request'}, status=400)
	else:
		return JsonResponse({'success': False, 'message': 'method not allowed'}, status=403)