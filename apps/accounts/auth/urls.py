from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.auth import views

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login_api'),
    path('register/', views.RegisterUserApiView.as_view()),
    path('register/verify_user/', views.VerifyUserApiView.as_view()),
    path('register/regenerate_code/', views.RegenerateCodeApiView.as_view()),
    path('register/complete_profile/<uuid:id>/', views.CompleteUserProfileApiView.as_view()),
    path('register/enter_user_password/<uuid:id>/', views.EnterUserPasswordApiView.as_view()),
    path('password/forgot_password/', views.ForgotPasswordApiView.as_view()),
    path('password/reset_password/<uuid:user_id>/<str:token>/', views.ResetPasswordApiView.as_view()),
]