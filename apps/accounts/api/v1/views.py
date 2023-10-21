from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

# para comprobar token
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from apps.accounts.serializers import UserSerializer, EspecialistaCreateSerializer

User = get_user_model()

# Create your views here.
@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        response = {"detail": "No Encontrado pass"}
        status_res = status.HTTP_404_NOT_FOUND
    else:
        token, created = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        # response = {"token": token.key, "user": serializer.data}
        response = {**serializer.data, "token": token.key}
        status_res = status.HTTP_200_OK
    return Response(response, status=status_res)
    

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.get(user=user)
        response = {**serializer.data, "token": token.key}
        status_res = status.HTTP_201_CREATED
    else:
        # response = serializer.errors
        response = {"msg": serializer.errors}
        status_res = status.HTTP_400_BAD_REQUEST
    return Response(response, status=status_res)
    

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response(f"passed for {request.user.email}")


@api_view(['POST'])
def especialista_create(request):
    serializer = EspecialistaCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.get(user=user)
        response = {**serializer.data, "token": token.key}
        status_res = status.HTTP_201_CREATED
    else:
        # response = serializer.errors
        response = {"msg": serializer.errors}
        status_res = status.HTTP_400_BAD_REQUEST
    return Response(response, status=status_res)