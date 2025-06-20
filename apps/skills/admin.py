from django.contrib import admin

from apps.skills import models


@admin.register(models.Skill)
class SkillsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']