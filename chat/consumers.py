import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # FETCH HISTORY: Grab old messages and send them immediately upon connecting
        history = await self.get_message_history()
        for msg in history:
            await self.send(text_data=json.dumps({
                'message': msg['content'],
                'username': msg['username']
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json.get('username', 'Anonymous')

        # SAVE TO DB: Store the message permanently
        await self.save_message(username, message)

        # Broadcast live to everyone else
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    # --- ASYNC DATABASE HELPERS ---
    
    @database_sync_to_async
    def get_message_history(self):
        room, created = Room.objects.get_or_create(name=self.room_name)
        # Get the last 50 messages
        messages = Message.objects.filter(room=room).order_by('timestamp')[:50]
        return [{'username': m.username, 'content': m.content} for m in messages]

    @database_sync_to_async
    def save_message(self, username, content):
        room, created = Room.objects.get_or_create(name=self.room_name)
        Message.objects.create(room=room, username=username, content=content)
