from rest_framework import generics, permissions

from apps.skills import models, serializers


class SkillListApiView(generics.ListAPIView):
    queryset = models.Skill.objects.all()
    serializer_class = serializers.SkillListSerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryListApiView(generics.ListAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategoryListSerializer
    permission_classes = [permissions.IsAuthenticated]