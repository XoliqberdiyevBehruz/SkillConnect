import json 

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from apps.chat import models


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # join room group 
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        # leave group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # messagelarni websocketdan qabul qilish 
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # send message to romm group
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'chat_message', 'message': message}
        )
    
    # messagelarni room groupdan qabul qilish 
    async def chat_message(self, event):
        message = event['message']

        # send message to websocket
        await self.send(text_data=json.dumps({"message": message}))

    
class GroupChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'group_chat_{self.group_id}'
        
        if not await self.group_exists(self.group_id):
            await self.close()
            return 

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        last_messages = await self.last_messages()

        last_messages = list(reversed(last_messages))
        await self.send_json({
            "type": "message_history",
            "messages": [
                {
                    "id": str(msg.id),
                    "message": msg.message,
                    "sender": msg.sender.email,
                    "created_at": str(msg.created_at),
                }
                for msg in last_messages
            ]
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        if not text_data:
            return 
        
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_json({"error": "Invalid JSON"})
            return 
    
        message = data.get('message')
        if not message:
            await self.send_json({"error": "Message is required"})
            return 
        
        saved_message = await self.message_save(message, self.user)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "group_chat_message",
                'id': str(saved_message.id),
                "message": saved_message.message,
                'sender_email': saved_message.sender.email,
                'created_at': str(saved_message.created_at),
            }
        )

    async def group_chat_message(self, event):
        await self.send_json({
            'id': event['id'],
            "message": event['message'],
            'sender': event['sender_email'],
            'created_at': event['created_at']
        })

    @database_sync_to_async
    def group_exists(self, group_id):
        return models.Group.objects.filter(id=group_id).exists()
    
    @database_sync_to_async
    def message_save(self, message, user):
        group = models.Group.objects.get(id=self.group_id)
        return models.Message.objects.create(chat=group, message=message, sender=user)
    
    @database_sync_to_async
    def last_messages(self,limit=50):
        return list(models.Message.objects.filter(chat=self.group_id).select_related('sender').order_by('-created_at')[:limit])
    