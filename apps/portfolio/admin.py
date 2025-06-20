from django.contrib import admin

from apps.portfolio import models


@admin.register(models.Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'likes_count']


@admin.register(models.PortfoliLike)
class PortfolioLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'portfolio']