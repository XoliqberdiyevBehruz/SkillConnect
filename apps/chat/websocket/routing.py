from django.urls import re_path

from apps.chat.websocket import consumers

websocker_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/group/(?P<group_id>[0-9a-f-]+)/$', consumers.GroupChatConsumer.as_asgi()),
]