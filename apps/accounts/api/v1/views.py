from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Q # Global search
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token

# para comprobar token
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers import ( 
    UserSerializer, EspecialistaCreateSerializer,
    EspecialistaUpdateSerializer,
    UserRegisterSerializer, UserLoginSerializer,
    User2Serializer, UserRegisterSerializer2,
    EspecialistaProfileSerializer, UserProfileSerializer
)

from apps.accounts.models import Especialista, EspecialistaProfile
from apps.core.mixins import PaginationMixins
from apps.booking.mixins import CustomUserPassesTestMixin


User = get_user_model()
# VERSION 1 generar token manual authtoken

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


@api_view(['GET'])
@permission_classes([AllowAny])
def especialistas_especialidad_json(request):
    especialidad = request.GET.get('especialidad')
    try:
        especialistas = Especialista.objects.all()
        if especialidad:
            print('Su especialidad es: ', especialidad)
            especialistas = especialistas.filter(especialistaprofile__especialidades__id=especialidad)
            print(especialistas)
            serializer = EspecialistaCreateSerializer(especialistas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        data = {"msg": 'Error inesperado, Intente mas tarde'}
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== ESPECIALISTAS ========== |
class EspecialistaListCreateAPIView(PaginationMixins, APIView):
    def get(self, request, *args, **kwargs):
        especialistas = Especialista.objects.all()

        orden = request.GET.get('orden')
        rango_fecha = request.GET.get('rango_fecha')
        q = request.GET.get('q')

        if q:
            especialistas = especialistas.filter(
                Q(id__icontains=q) |
                # Q(especialidades__nombre__icontains=q) |
                # Q(user__username__icontains=q)
                Q(username__icontains=q) | 
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
        if orden:
            if orden == 'asc':
                especialistas = especialistas.order_by('date_joined')
            else:
                especialistas = especialistas.order_by('-date_joined')

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            especialistas = especialistas.filter(date_joined__range=[fechas[0], fechas[1]])

        # Filtros especificos
        especialidad = request.GET.get('especialidad')
        if especialidad:
            print('Su especialidad es: ', especialidad)
            especialistas = especialistas.filter(especialistaprofile__especialidades__id=especialidad)
            print(especialistas)

        try:
            # Obtener la página actual
            page = self.paginate_queryset(especialistas, request)
            if page is not None:
                # Serializer tus datos como de costumbre
                serializer = EspecialistaCreateSerializer(page, many=True)
    
                # Devolver los datos paginados junto con los metadatos
                data = self.get_paginated_response(serializer.data)
                return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            data = {"msg": 'Error inesperado, Intente mas tarde'}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            profile_serializer = EspecialistaProfileSerializer(data=request.data)
            especialista_serializer = EspecialistaCreateSerializer(data=request.data)
            especialista_valid = especialista_serializer.is_valid()
            profile_valid = profile_serializer.is_valid()
            if especialista_valid and profile_valid:
                especialista = especialista_serializer.save()
                profile_serializer.save(user=especialista)
                # token = Token.objects.get(user=user)
                # response = {**serializer.data, "token": token.key}
                refresh = RefreshToken.for_user(especialista)
                token = {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
                data = {**especialista_serializer.data, **profile_serializer.data,  "token": token}
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                errors = {}
                if not especialista_valid:
                    errors = {**especialista_serializer.errors}
                if not profile_valid:
                    errors = {**errors, **profile_serializer.errors}

                error_messages = []
                for field, errors in errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                data = {"msg": error_messages}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            data = {"msg": 'Error inesperado, Intente mas tarde'}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EspecialistaRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, APIView):
    # list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        try:
            especialista = Especialista.objects.get(id=kwargs.get('id'))
            serializer = EspecialistaCreateSerializer(especialista)
            return Response(serializer.dat, status=status.HTTP_200_OK)
        except Especialista.DoesNotExist:
            print('El Especialista no existe')
            data = {'msg': 'Especialista No Encontrado'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            data = {"msg": 'Error inesperado, Intente mas tarde'}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, *args, **kwargs):
        try:
            especialista = Especialista.objects.get(pk=kwargs.get('id'))
            especialista_profile = EspecialistaProfile.objects.get(user=especialista.id)
            profile_serializer = EspecialistaProfileSerializer(data=request.data, instance=especialista_profile)
            especialista_serializer = EspecialistaUpdateSerializer(data=request.data, instance=especialista)
            especialista_valid = especialista_serializer.is_valid()
            profile_valid = profile_serializer.is_valid()
            if especialista_valid and profile_valid:
                especialista = especialista_serializer.save()
                profile_serializer.save(user=especialista)
                # token = Token.objects.get(user=user)
                # response = {**serializer.data, "token": token.key}
                refresh = RefreshToken.for_user(especialista)
                token = {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
                data = {**especialista_serializer.data, **profile_serializer.data,  "token": token}
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                errors = {}
                if not especialista_valid:
                    errors = {**especialista_serializer.errors}
                if not profile_valid:
                    errors = {**errors, **profile_serializer.errors}

                error_messages = []
                for field, errors in errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                data = {"msg": error_messages}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            data = {"msg": 'Error inesperado, Intente mas tarde'}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            especialista = Especialista.objects.get(pk=kwargs.get('id'))
            especialista.delete()
            data = {'msg': 'Especialista Eliminado Correctamente'}  # con este estatus 204 no se devuelve el response
            return Response(data, status=status.HTTP_200_OK)
        except Especialista.DoesNotExist:
            print('La Especialista no existe')
            data = {'msg': 'Especialista No Encontrado'}
            return Response(data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            data = {"msg": 'Error inesperado, Intente mas tarde'}
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# VERSION 2  generar token manual authtoken
class UserRegister(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # token = Token.objects.get(user=user)
            # data = {**serializer.data, "token": token.key}
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        data = {"msg": serializer.errors}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.check_user(request.data)
            print(user)
            login(request, user)
            # token, created = Token.objects.get_or_create(user=user)
            # data = {**serializer.data, "token": token.key}
            return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogout(APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (SessionAuthentication, )

    def get(self, request, *args, **kwargs):
        serializer = User2Serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# VERSION 3  generar token manual authtoken
@api_view(['POST'])
def logout(request):
    if request.method == "POST":
        request.user.auth_token.delete()
        return Response({"msg": 'Tu te deslogueaste'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def user_register(request):
    if request.method == 'POST':
        serializer = UserRegisterSerializer2(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # token = Token.objects.get(user=user)
            # data = {**serializer.data, "token": token.key}
            refresh = RefreshToken.for_user(user)
            token = {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
            data = {**serializer.data, "token": token}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# usandola con JWT
class UserProfile(APIView):

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)