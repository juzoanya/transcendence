import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings


User = settings.AUTH_USER_MODEL

# class PublicChatConsumer(AsyncJsonWebsocketConsumer):

#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
#         self.room_group_name = f"chat_{self.room_name}"

#         print("PublicChatConsumer: connect: " + str(self.scope['user']))
#         await self.accept()

#     async def disconnect(self, code):
#         print("PublicChatConsumer: disconnect")
#         pass

#     async def receive_json(self, content):
#         command = content.get('command', None)
#         print("PublicChatConsumer: command: " + str(command))

# chat/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer



class PublicChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
