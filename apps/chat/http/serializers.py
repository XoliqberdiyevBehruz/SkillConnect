from django.db import transaction

from rest_framework import serializers

from apps.chat import models
from apps.accounts.models import User

class GroupCreateSerializer(serializers.Serializer):
    members_ids = serializers.ListSerializer(child=serializers.UUIDField())
    group_name = serializers.CharField()

    def create(self, validated_data):
        with transaction.atomic():
            group = models.Group.objects.create(
                name=validated_data.get('group_name'),
            )
            group.members.set(validated_data.pop('members_ids')),
            return group


class MemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = [
            'id', 'email', 'full_name'
        ]    
    
class GroupListSerializer(serializers.ModelSerializer):
    members = MemberListSerializer(many=True)
    
    class Meta:
        model = models.Group
        fields = [
            'id', 'name', 'members'
        ]