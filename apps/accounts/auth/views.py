from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, status, permissions, parsers
from rest_framework.response import Response

from apps.accounts.auth import serializers
from apps.accounts import models, tasks


class RegisterUserApiView(generics.GenericAPIView):
    serializer_class = serializers.RegisterByEmailSerializer
    queryset = models.User.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            res = serializer.save()
            transaction.on_commit(lambda: tasks.send_code_to_email.delay(res.get('code'), res.get('email')))
            return Response(res, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserApiView(generics.GenericAPIView):
    serializer_class = serializers.VerifyUserSerializer
    queryset = models.User.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({"message": "User successfully verified"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RegenerateCodeApiView(generics.GenericAPIView):
    serializer_class = serializers.RegenerateCodeSerializer
    queryset = models.User.objects.all()
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            res = serializer.save()
            transaction.on_commit(lambda: tasks.send_code_to_email.delay(res.get('code'), res.get('email')))
            return Response(
                res,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_200_OK)
    

class CompleteUserProfileApiView(generics.GenericAPIView):
    serializer_class = serializers.CompleteUserProfileSerializer
    queryset = models.User.objects.all()
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def put(self, request, id):
        user = get_object_or_404(models.User, id=id)
        serializer = self.serializer_class(user, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Profile complited"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    