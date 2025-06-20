from django.urls import path, include

from apps.portfolio import views


urlpatterns = [
    path("portfolio/create/", views.PortfoliCreateApiView.as_view()),
    path('portfolio/<uuid:id>/update/', views.PortfolioUpdateApiView.as_view()),
    path('portfolio/<uuid:id>/delete/', views.PortfolioDeleteApiView.as_view()),
    path('portfolio/<uuid:id>/like/', views.PortfolioLikeApiView.as_view()),    
    path('<uuid:user_id>/portfolio/list/', views.PortfolioListApiView.as_view()),
]