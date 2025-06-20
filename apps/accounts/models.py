import sys, random
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.shared.models import BaseModel, Region, City
from apps.accounts.managers import CustomUserManager
from apps.skills.models import Category, Skill

FREELANCER, COMPANY, ADMIN = ('freelancer', 'company', 'admin')


class User(AbstractUser, BaseModel):
    ROLE = (
        (FREELANCER, 'freelancer'),
        (COMPANY, 'company'),
        (ADMIN, 'admin'),
    )

    full_name = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="apps/accounts/user/avatar/%Y/%m", null=True, blank=True)
    bio = models.TextField()
    
    is_verified = models.BooleanField(default=False)

    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, null=True)
    skills = models.ManyToManyField(Skill, related_name="users")
    city = models.ForeignKey(
        City, on_delete=models.DO_NOTHING, related_name='cities', null=True, blank=True
    )
    region = models.ForeignKey(
        Region, on_delete=models.DO_NOTHING, related_name='regions', null=True, blank=True
    )
    
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = None
    first_name = None
    last_name = None

    def __str__(self):
        return self.full_name
    
    def generate_verification_code(self):
        code = "".join([str(random.randint(1, 10)%10) for _ in range(5)])
        verification = UserVerification.objects.create(
            code=code, user=self, expired_at=timezone.now() + timedelta(minutes=5)
        )
        return verification.code

    def save(self, *args, **kwargs):
        if 'createsuperuser' in sys.argv:
            return super().save(*args, **kwargs)
        if self.region and self.city:
            if self.region.city.id != self.city.id:
                raise ValidationError("The region does not belong to city!")
            
        return super().save(*args, **kwargs)


class Link(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='links')
    github = models.URLField()
    linkedin = models.URLField()

    def __str__(self):
        return f'{self.user.full_name} github link - {self.github}'
    

class UserVerification(BaseModel):
    code = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    expired_at = models.DateTimeField()
    is_confirm = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} verification code is - {self.code}, expired at {self.expired_at}" 