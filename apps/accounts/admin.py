from django.contrib import admin

from apps.accounts import models


admin.site.register(models.User)
admin.site.register(models.UserVerification)