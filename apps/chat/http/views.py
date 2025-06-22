from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.response import Response

from apps.chat import models
from apps.chat.http import serializers
from apps.accounts.models import User


class GroupCreateApiView(generics.CreateAPIView):
    serializer_class = serializers.GroupCreateSerializer
    queryset = models.Group.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class GroupListApiView(generics.GenericAPIView):
    serializer_class = serializers.GroupListSerializer

    def get(self, request, member_id):
        user = get_object_or_404(User, id=member_id)
        groups = models.Group.objects.filter(members=user)  
        serializer = self.serializer_class(groups, many=True)
        return Response(serializer.data, status=200)