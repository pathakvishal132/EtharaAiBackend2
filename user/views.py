from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import UserSerializer
from django.http import HttpResponse, JsonResponse
from .models import User
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.conf import settings
import jwt
import datetime


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse(serializer.data)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            raise ValidationError("Email and password are required")

        try:
            user = User.objects.get(email=email)

            if not user.check_password(password):
                raise AuthenticationFailed("Password is incorrect")
            payload = {
                "id": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                "iat": datetime.datetime.utcnow()
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            response = Response()
            response.set_cookie(key='jwt', value=token, httponly=True, samesite='None', secure=True)
            response.data = {
                'jwt': token
            }
            return response

        except User.DoesNotExist:
            raise ValidationError("User not found")


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Unauthenticated")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['id'])
        serialiser = UserSerializer(user)
        return Response(serialiser.data)
