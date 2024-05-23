
from django.urls import re_path, path
from . import consumers
from . import views

websocket_urlpatterns = [
    re_path(r'public_chat/(?P<room_id>\w+)/$', consumers.PublicChatConsumer.as_asgi()),
]

urlpatterns = [
    path('', views.public_chat_view, name='public-chat'),

]