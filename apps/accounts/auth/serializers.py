from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from apps.accounts import models 
from apps.shared.models import City, Region


class RegisterByEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField()

    def validate(self, data):
        try:
            user = models.User.objects.get(email=data.get('email'))
        except models.User.DoesNotExist:
            return data
        else:
            raise serializers.ValidationError("User with this email already exists!")

    def create(self, validated_data):
        with transaction.atomic():
            user = models.User.objects.create(
                email=validated_data.get('email'),
                full_name=validated_data.get('full_name')
            )
            data = {
                'id': str(user.id),
                'email': user.email,
                'code': user.generate_verification_code()
            }
            return data
        
    
class VerifyUserSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = models.User.objects.get(email=data.get('email'))
            verification = models.UserVerification.objects.get(code=data.get('code'), user=user)
        except models.User.DoesNotExist:
            raise serializers.ValidationError("User not found!")
        except models.UserVerification.DoesNotExist:
            raise serializers.ValidationError("Code is incorrect!")
        if user.is_verified:
            raise serializers.ValidationError("User already verified!")
        if verification.expired_at < timezone.now():
            raise serializers.ValidationError("Code is expired!")
        else:
            verification.is_confirm = True
            verification.save()
            user.is_verified = True
            user.save()
        return data
    

class RegenerateCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = models.User.objects.get(email=data.get('email'))
        except models.User.DoesNotExist:
            raise serializers.ValidationError("User not found!")
        if user.is_verified:
            raise serializers.ValidationError("User already verified!")
        verification = models.UserVerification.objects.filter(user=user).order_by('-created_at').first()
        if verification and verification.expired_at > timezone.now():
            raise serializers.ValidationError("The code is still valid")
        data['user'] = user
        return data
    

    def save(self, **kwargs):
        user = self.validated_data.get('user')
        return {
            'id': str(user.id),
            'code': user.generate_verification_code(),
            'email': user.email
        }
    

class CompleteUserProfileSerializer(serializers.ModelSerializer):
    city_id = serializers.UUIDField()
    region_id = serializers.UUIDField()

    class Meta:
        model = models.User
        fields = [
            'avatar', 'bio', 'city_id', 'region_id'
        ]

    def validate(self, data):
        try:
            city = City.objects.get(id=data.get('city_id'))
            region = Region.objects.get(id=data.get('region_id'))
        except City.DoesNotExist:
            raise serializers.ValidationError("City not found!")
        except Region.DoesNotExist:
            raise serializers.ValidationError("Region not found!")
        if region.city != city:
            raise serializers.ValidationError("The region does not belong to city!")
        data['city'] = city
        data['region'] = region
        return data

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.avatar = validated_data.get('avatar')
            instance.bio = validated_data.get('bio')
            instance.city = validated_data.get('city')
            instance.region = validated_data.get('region')
            instance.save()
            return instance
        
    
class EnterUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Two password must be same!")
        if len(data.get('password')) < 6:
            raise serializers.ValidationError("Password min length is 6!")
        if data.get('password').isdigit():
            raise serializers.ValidationError("Password is to numeric!")
        return data
    
    def update(self, instance, validated_data):
        instance.password = make_password(validated_data.get('password'))
        instance.save()
        return instance
    

class ForgotPassword(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6)
    confirm_password = serializers.CharField(min_length=6)

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError("Password do not match!")
        return data