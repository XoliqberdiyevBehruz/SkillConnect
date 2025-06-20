from django.shortcuts import get_object_or_404
from django.db.models import F

from rest_framework import generics, views, permissions, parsers
from rest_framework.response import Response

from apps.portfolio import serializers, models
from apps.accounts.models import User


class PortfoliCreateApiView(generics.CreateAPIView):
    queryset = models.Portfolio.objects.all()
    serializer_class = serializers.PortfoliCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context    


class PortfolioListApiView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        portfolios = models.Portfolio.objects.filter(user=user)
        serializer = serializers.PortfoliListSerializer(portfolios, many=True)
        return Response(serializer.data, status=200)


class PortfolioUpdateApiView(generics.GenericAPIView):
    serializer_class = serializers.PortfolioUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.FormParser, parsers.MultiPartParser]

    def patch(self, request, id):
        user = request.user
        portfolio = get_object_or_404(models.Portfolio, id=id)
        if portfolio.user != user:
            return Response({"message": "you cannot update this portfolio"}, status=400)
        serializer = self.serializer_class(portfolio, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"status": True}, status=200)
        return Response(serializer.errors, status=400)
    

class PortfolioDeleteApiView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, id):
        user = request.user
        portfolio = get_object_or_404(models.Portfolio, id=id)
        if portfolio.user != user:
            return Response({"message": "you cannot delete this portfolio"}, status=400)
        portfolio.delete()
        return Response({"message": 'deleted!'}, status=203)


class PortfolioLikeApiView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        portfolio = get_object_or_404(models.Portfolio, id=id)
        user = request.user
        if portfolio.user == user:
            return Response({'message': "you cannot like your portfolio"}, status=400)
        like, created = models.PortfoliLike.objects.get_or_create(user=user, portfolio=portfolio)
        res = {}
        if created: 
            portfolio.likes_count = F("likes_count") + 1
            res = {"liked": True}
        else:
            res = {'liked': False}
            portfolio.likes_count = F('likes_count') - 1
            like.delete()
        portfolio.save(update_fields=['likes_count'])
        return Response(res, status=200)

