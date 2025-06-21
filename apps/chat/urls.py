from django.urls import path

from apps.chat import views

urlpatterns = [
    path('', views.index),
    path('<str:room_name>/', views.room),
]