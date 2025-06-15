from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.auth import views

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login_api'),
    path('register/', views.RegisterUserApiView.as_view()),
    path('verify_user/', views.VerifyUserApiView.as_view()),
    path('regenerate_code/', views.RegenerateCodeApiView.as_view()),
    path('complete_profile/<uuid:id>/', views.CompleteUserProfileApiView.as_view()),
]