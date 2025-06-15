import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(editable=False, db_index=True, default=uuid.uuid4, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    
class City(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Region(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='regions')

    def __str__(self):
        return f'{self.city.name} - {self.name}'
    