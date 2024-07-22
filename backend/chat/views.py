import json
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from user.utils import *
from .models import *
from .utils import *
from friends.models import FriendList
from django.views.decorators.http import require_GET, require_POST, require_safe
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

Debug = True

def chat_view(request):
	context = {}
	context['debug_mode'] = settings.DEBUG
	context['room_type'] = 'public'
	context['room_id'] = 1
	context['debug'] = Debug
	user = request.user
	room_id = context['room_id']
	chat_room = ChatRoom.objects.get(id=room_id)
	chat_messages = ChatMessage.objects.filter(room=chat_room)[:30]
	messages = []
	for chat in chat_messages:
		item = model_object_serializer(chat)
		messages.append(item)
	context['messages'] = messages
	# return JsonResponse({'success': True, 'message': messages}, status=200)
	return render(request, "chats/public-chat.html", context)


@csrf_exempt
@login_required
@require_GET
def chat_room_get(request, *args, **kwargs):
	user = request.user
	# friend_id = json.loads(request.body).get('user_id')
	friend_id = kwargs.get('user_id')
	print(f'---->> friend_id')
	try:
		friend = UserAccount.objects.get(pk=friend_id)
		friend_list = FriendList.objects.get(user=user)
	except Exception as e:
		return InternalServerError500(message=str(e))
	print(f'---->> progress')
	if not friend_list.is_mutual_friend(friend):
		return Forbidden403(message=f'Access denied: you must be friends to chat {friend}')
	try:
		room = get_private_room_or_create(user, friend)
		print(f'---->> got room')
	except Exception as e:
		return InternalServerError500(message=str(e))
	data = {}
	if room.id:
		data['room_id'] = room.id
	return Success200(message='', data=data)


