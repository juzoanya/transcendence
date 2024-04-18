import json
from django.shortcuts import render
from .models import FriendList, FriendRequest
from user.models import UserAccount
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder


# Create your views here.


@login_required
def friend_list(request, *args, **kwargs):
    pass

@login_required
def accept_friend_request(request, *args, **kwargs):
    pass


@login_required
def reject_friend_request(request, *args, **kwargs):
    pass


@login_required
def cancel_friend_request(request, *args, **kwargs):
    pass



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
                'pk': req.receiver.pk,
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
                'pk': req.sender.pk,
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
            return JsonResponse({'success': False, 'message': 'User does not exist'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'method not allowed'}, status=403)