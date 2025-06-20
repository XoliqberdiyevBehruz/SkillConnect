from rest_framework import serializers

from apps.skills import models


class SkillListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Skill
        fields = ['id', 'name']
    

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'name']