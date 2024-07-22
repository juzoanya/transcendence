
from django.urls import re_path, path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('room/<user_id>', views.chat_room_get, name='room-get'),

]