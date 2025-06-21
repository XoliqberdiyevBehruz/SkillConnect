import json 

from django.contrib.auth.models import AnonymousUser

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
        
        if self.user == AnonymousUser():
            await self.close()
            return

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
        readed_messages = []
        unreaded_messages = []
        for msg in last_messages:
            message = {
                "id": str(msg.id),
                "message": msg.message,
                'sender': {
                    "id": str(msg.sender.id),
                    "email": msg.sender.email,
                    "full_name": msg.sender.full_name
                },
                "is_updated": msg.is_updated,
                "is_read": msg.is_read,
                "created_at": str(msg.created_at),
            }
            if msg.is_read:
                readed_messages.append(message)
            else:
                unreaded_messages.append(message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "group_message_history",
                "readed_messages": readed_messages,
                "unreaded_messages": unreaded_messages
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if not action:
            await self.send_json({"error": 'action is required'})
            return
        
        elif action == "send":
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
                    'sender': {
                        "id": str(saved_message.sender.id),
                        "email": saved_message.sender.email,
                        "full_name": saved_message.sender.full_name
                    },
                    'is_updated': saved_message.is_updated,
                    'is_read': saved_message.is_read,
                    'created_at': str(saved_message.created_at),
                }
            )
        
        elif action == 'read':
            message_id = data.get('message_id')
            if not message_id:
                await self.send_json({'error': "message_id is required"})    
                return
            else:
                res = await self.mark_message_as_read(message_id)
                if res:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "group_chat_message",
                            'id': str(saved_message.id),
                            "message": saved_message.message,
                            'sender': {
                                "id": str(saved_message.sender.id),
                                "email": saved_message.sender.email,
                                "full_name": saved_message.sender.full_name
                            },
                            'is_updated': saved_message.is_updated,
                            'is_read': saved_message.is_read,
                            'created_at': str(saved_message.created_at),
                        }
                    )
                else:
                    await self.send_json({'message': 'you cannot read your message'})

        elif action == "delete":
            message_id = data.get("message_id")
            if message_id:
                res = await self.delete_message(message_id)
                if res:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "group_chat_message",
                            'id': str(saved_message.id),
                            "message": saved_message.message,
                            'sender': {
                                "id": str(saved_message.sender.id),
                                "email": saved_message.sender.email,
                                "full_name": saved_message.sender.full_name
                            },
                            'is_updated': saved_message.is_updated,
                            'is_read': saved_message.is_read,
                            'created_at': str(saved_message.created_at),
                        }
                    )
                else:
                    self.send_json({"error": "you cannot delete this message, this is another member's message"})
            else:
                await self.send_json({"error": "message_id required"})

        elif action == "update":
            message_id = data.get('message_id')
            new_message = data.get('new_message')
            if message_id:
                message = await self.edit_message(message_id, new_message)
                if message:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "group_chat_message",
                            'id': str(message.id),
                            "message": message.message,
                            'sender': {
                                "id": str(message.sender.id),
                                "email": message.sender.email,
                                "full_name": message.sender.full_name
                            },
                            'is_updated': message.is_updated,
                            'is_read': message.is_read,
                            'created_at': str(message.created_at),
                        }
                    )
                else:
                    await self.send_json({'error': "you cannot updated this message, this is another member's meesage"})
                    return 
            else:
                await self.send_json({"error": "message_id and new_message is required"})
                return 

        else:
            await self.send_json({"error": "choose action(read, send)"})
            return

    async def group_chat_message(self, event):
        await self.send_json({
            'id': event['id'],
            "message": event['message'],
            'sender': {
                "id": event["sender"]['id'],
                "email": event["sender"]['email'],
                "full_name": event["sender"]['full_name']
            },
            'is_updated': event['is_updated'],
            'is_read': event['is_read'],
            'created_at': event['created_at']
        })

    async def group_message_history(self, event):
        await self.send_json({
            "readed_messages": event['readed_messages'],
            "unreaded_messages": event['unreaded_messages']
        })

    @database_sync_to_async
    def group_exists(self, group_id):
        return models.Group.objects.filter(id=group_id, members=self.user).exists()
    
    @database_sync_to_async
    def message_save(self, message, user):
        group = models.Group.objects.get(id=self.group_id)
        return models.Message.objects.create(chat=group, message=message, sender=user)
    
    @database_sync_to_async
    def last_messages(self,limit=50):
        return list(models.Message.objects.filter(chat=self.group_id).select_related('sender').order_by('-created_at')[:limit])
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        message =  models.Message.objects.get(id=message_id)
        if message.sender != self.user:
            message.is_read = True
            message.save()
            return True
        else:
            return False
    
    @database_sync_to_async
    def edit_message(self, message_id, new_text):
        try:
            message =  models.Message.objects.get(id=message_id)
        except models.Message.DoesNotExist:
            return False
        if message.sender == self.user:    
            message.message = new_text
            message.is_updated = True
            message.save()
            return message
        else:
            return False
        
    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            message = models.Message.objects.get(id=message_id)
        except models.Message.DoesNotExist:
            return False
        if message.sender == self.user:
            message.delete()
            return True
        else:
            return False