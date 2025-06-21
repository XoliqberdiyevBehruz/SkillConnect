from django.contrib import admin

from apps.chat import models


admin.site.register(models.Group)
admin.site.register(models.Message)