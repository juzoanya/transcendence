from django.shortcuts import render
from django.conf import settings

def public_chat_view(request):
	context = {}
	context['debug_mode'] = settings.DEBUG
	context['room_id'] = 1
	return render(request, "chats/public-chat.html", context)
