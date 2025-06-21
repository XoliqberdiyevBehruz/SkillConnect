from django.db import models

from apps.shared.models import BaseModel
from apps.accounts.models import User

class Group(BaseModel):
    members = models.ManyToManyField(User, related_name='chat_groups')
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Message(BaseModel):
    chat = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_updated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} - {self.message}'