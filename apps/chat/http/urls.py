from django.urls import path

from apps.chat.http import views

urlpatterns = [
    path('group/create/', views.GroupCreateApiView.as_view()),
    path('<uuid:member_id>/group/list/', views.GroupListApiView.as_view()),
]