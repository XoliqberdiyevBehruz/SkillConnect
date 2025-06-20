from django.urls import path, include


from apps.skills import views


urlpatterns = [
    path('category/list/', views.CategoryListApiView.as_view()),
    path('skill/list/', views.SkillListApiView.as_view()),
]