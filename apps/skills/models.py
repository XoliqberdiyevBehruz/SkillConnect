from django.db import models

from apps.shared.models import BaseModel


class Skill(BaseModel):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name