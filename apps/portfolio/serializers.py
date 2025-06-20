from django.db import transaction
from django.db.models import F

from rest_framework import serializers

from apps.portfolio.models import PortfoliLike, Portfolio
from apps.accounts.models import User

class PortfoliCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    image = serializers.ImageField()
    description = serializers.CharField()
    link = serializers.URLField()
    
    def create(self, validated_data):
        with transaction.atomic():
            portfoli = Portfolio.objects.create(
                user=self.context.get("user"),
                title=validated_data.get('title'),
                description=validated_data.get('description'),
                link=validated_data.get('link'),
                image=validated_data.get('image')
            )
            return portfoli
    

class PortfoliListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = [
            'id', 'title', 'description', 'link', 'image', 'likes_count', 'created_at'
        ]
    

class PortfolioUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    link = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.title = validated_data.get('title', instance.title)
            instance.description = validated_data.get('description', instance.description)
            instance.link = validated_data.get('link', instance.link)
            instance.image = validated_data.get('image', instance.image)
            instance.save()
            return instance
        
    
class PortfoliLikeSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    portfoli_id = serializers.UUIDField()
