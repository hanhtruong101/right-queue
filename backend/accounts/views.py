from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout,
)
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, CurrentUserSerializer

class CsrfView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        csrf_token = get_token(request)

        return Response(
            {"csrf_token": csrf_token},
            status=status.HTTP_200_OK,
        )

@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    authentication_classes=[]
    permission_classes = [AllowAny]

    def post(self, request):
        input_serializer=LoginSerializer(data = request.data)
        input_serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            username=input_serializer.validated_data["username"],
            password=input_serializer.validated_data["password"],
        )

        if user is None:
            raise ValidationError({
                "detail": ("The username or password is incorrect.")
            })

        django_login(request, user)

        output_serializer = CurrentUserSerializer(user)

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )

class CurrentUserView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer= CurrentUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK,)

class LogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request): 
        django_logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)
    