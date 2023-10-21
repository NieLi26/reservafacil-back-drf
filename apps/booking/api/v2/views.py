import json
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from datetime import date, datetime, timedelta
from django.db.models import Q, F  # Global search
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from apps.booking.utils import (
    validar_citas_cliente_fecha,
    validar_cita_confirmada
)
from apps.booking.mixins import PaginationMixin, CustomUserPassesTestMixin
from apps.accounts.models import EspecialistaProfile, Especialista
from apps.accounts.forms import EspecialistaProfileForm, EspecialistaCreationForm, EspecialistaChangeForm
from apps.booking.models import (
    Categoria, Especialidad, Cliente,
    Cita, Horario, Pago, HistorialAnulacion,
    Tarifa
)

from apps.booking.serializers import (
    TarifaSerializer, CategoriaSerializer,
    ClienteSerializer, EspecialidadSerializer,
    HorarioSerializer, PagoSerializer,
    CitaCreateSerializer, HistorialAnulacionSerializer
)

from apps.accounts.serializers import EspecialistaCreateSerializer

from apps.accounts.models import EspecialistaProfile


class PaginationMixins(PageNumberPagination):
    page_size = 2

    def get_paginated_response(self, data):
        return {
            'number': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'has_previous': self.page.has_previous(),
            'has_next': self.page.has_next(),
            'paginate_by': self.page_size,
            'total_results': self.page.paginator.count,
            'start_index': self.page.start_index(),
            'end_index': self.page.end_index(),
            'results': data
        }

    # def get_paginated_response(self, data):
    #     return {
    #         'links': {
    #             'next': self.get_next_link(),
    #             'previous': self.get_previous_link()
    #         },
    #         'count': self.page.paginator.count,
    #         'results': data
    #     }


# @api_view(['GET', 'POST'])
# def reserve_list_create(request):
#     if request.method == 'GET':
#         reserve_list = Reserve.objects.all() 
#         serializer = CheckOutSerializer(reserve_list, many=True)

#         if serializer.data:
#             return Response(serializer.data)
#         return Response({'detail': "Not content"}, status=status.HTTP_200_OK)
    
#     elif request.method == 'POST':   
#         serializer = ReserveSerializer(data=request.data, context=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     else:
#         return Response({'Metodo no permitido'},status=status.HTTP_405_METHOD_NOT_ALLOWED)


# class ReservePeriodPagination(APIView):
#     def get(self, request, *args, **kwargs):
#         q = request.query_params.get('q', '')
#         reserve_list = ReservePeriod.objects.filter(licence__icontains=q)
#         paginator = PaginationMixin()
#         page_obj = paginator.paginate_queryset(reserve_list, request)
#         serializer = ReservePeriodSerializer(page_obj, many=True)
#         if serializer.data:
#             return paginator.get_paginated_response(serializer.data)
#         return Response({'detail': "Not content"}, status=status.HTTP_200_OK)



@api_view(['GET'])
def categorias_json(request):
    status_res = status.HTTP_200_OK
    # categorias = Categoria.objects.all()
    # data = [categoria.get_data() for categoria in categorias]
    try:
        response = list(Categoria.objects.values('id', 'nombre'))
    except Exception as e:
        print(str(e))
        response = {"msg": 'Error inesperado, Intente mas tarde'}
        status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response(response, status=status_res)


@api_view(['GET'])
def tarifas_json(request):
    status_res = status.HTTP_200_OK
    # categorias = Categoria.objects.all()
    # data = [categoria.get_data() for categoria in categorias]
    try:
        response = list(Tarifa.objects.values('id', 'valor'))
    except Exception as e:
        print(str(e))
        response = {"msg": 'Error inesperado, Intente mas tarde'}
        status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response(response, status=status_res)


@api_view(['GET'])
def especialistas_json(request):
    status_res = status.HTTP_200_OK
    # categorias = Categoria.objects.all()
    # data = [categoria.get_data() for categoria in categorias]
    try:
        response = list(EspecialistaProfile.objects.annotate(nombre=F('user__username')).values('id', 'nombre'))
    except Exception as e:
        print(str(e))
        response = {"msg": 'Error inesperado, Intente mas tarde'}
        status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response(response, status=status_res)


# ========== TARIFAS ========== |
class TarifaListCreateAPIView(PaginationMixins, APIView):
    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK

        tarifas = Tarifa.objects.all()

        orden = request.GET.get('orden')
        rango_fecha = request.GET.get('rango_fecha')
        q = request.GET.get('q')

        if q:
            tarifas = tarifas.filter(
                Q(id__icontains=q) |
                Q(valor__icontains=q)
            )
        if orden:
            if orden == 'asc':
                tarifas = tarifas.order_by('created')
            else:
                tarifas = tarifas.order_by('-created')

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            tarifas = tarifas.filter(created__range=[fechas[0], fechas[1]])

        try:
            # page_obj = self.paginate_queryset(tarifas, request)
            # serializer = TarifaSerializer(page_obj, many=True)
            # if serializer.data:
            #     print(self.get_paginated_response(serializer.data))
            #     print(type(self.get_paginated_response(serializer.data)))
            #     response['data'] = serializer.data
            #     response['paginator'] = self.get_paginated_response(serializer.data)
            # else:
            #     response['data'] = {'detail': "Not content"}

            # Obtener la página actual
            page = self.paginate_queryset(tarifas, request)
            if page is not None:
                # Serializer tus datos como de costumbre
                serializer = TarifaSerializer(page, many=True)
                
                # Devolver los datos paginados junto con los metadatos
                response = self.get_paginated_response(serializer.data)

        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        try:
            # serializer = TarifaSerializer(data=request.data, context=request.data)
            print(request.data, 'holaaa')
            serializer = TarifaSerializer(data=request.data, context=request.data)
            if serializer.is_valid():
                tarifa = serializer.save()
                print(TarifaSerializer(tarifa).data)
                response = TarifaSerializer(tarifa).data
            else:
                print(serializer.errors)
                print(serializer.errors['valor'])
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


class TarifaRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, APIView):
    # list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            tarifa = Tarifa.objects.get(id=id)
            serializer = TarifaSerializer(tarifa)
            response = serializer.data
        except Tarifa.DoesNotExist:
            print('La Tarifa no existe')
            response = {'msg': 'Tarifa No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def put(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            tarifa = Tarifa.objects.get(pk=id)
            serializer = TarifaSerializer(data=request.data, instance=tarifa)
            if serializer.is_valid():
                tarifa = serializer.save()
                response = TarifaSerializer(tarifa).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Tarifa.DoesNotExist:
            print('La Tarifa no existe')
            response = {'msg': 'Tarifa No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def delete(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            tarifa = Tarifa.objects.get(id=id)
            tarifa.delete()
            response = {'msg': 'Tarifa Eliminada Correctamente'} # con este estatus 204 no se devuelve el response
        except Tarifa.DoesNotExist:
            print('La Tarifa no existe')
            response = {'msg': 'Tarifa No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


# ========== CATEGORIAS ========== |
class CategoriaListCreateAPIView(PaginationMixins, APIView):
    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK

        categorias = Categoria.objects.all()

        orden = request.GET.get('orden')
        rango_fecha = request.GET.get('rango_fecha')
        q = request.GET.get('q')

        if q:
            categorias = categorias.filter(
                Q(id__icontains=q) |
                Q(nombre__icontains=q)
            )
        if orden:
            if orden == 'asc':
                categorias = categorias.order_by('created')
            else:
                categorias = categorias.order_by('-created')

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            categorias = categorias.filter(created__range=[fechas[0], fechas[1]])

        try:
            # page_obj = self.paginate_queryset(tarifas, request)
            # serializer = TarifaSerializer(page_obj, many=True)
            # if serializer.data:
            #     print(self.get_paginated_response(serializer.data))
            #     print(type(self.get_paginated_response(serializer.data)))
            #     response['data'] = serializer.data
            #     response['paginator'] = self.get_paginated_response(serializer.data)
            # else:
            #     response['data'] = {'detail': "Not content"}

            # Obtener la página actual
            page = self.paginate_queryset(categorias, request)
            if page is not None:
                # Serializer tus datos como de costumbre
                serializer = CategoriaSerializer(page, many=True)
                
                # Devolver los datos paginados junto con los metadatos
                response = self.get_paginated_response(serializer.data)

        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        try:
            serializer = CategoriaSerializer(data=request.data, context=request.data)
            if serializer.is_valid():
                categoria = serializer.save()
                print(CategoriaSerializer(categoria).data)
                response = CategoriaSerializer(categoria).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


class CategoriaRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, APIView):
    # list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            categoria = Categoria.objects.get(id=id)
            serializer = CategoriaSerializer(categoria)
            response = serializer.data
        except Categoria.DoesNotExist:
            print('La Categoria no existe')
            response = {'msg': 'Categoria No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def put(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            categoria = Categoria.objects.get(pk=id)
            serializer = CategoriaSerializer(data=request.data, instance=categoria)
            if serializer.is_valid():
                categoria = serializer.save()
                response = CategoriaSerializer(categoria).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Categoria.DoesNotExist:
            print('La Tarifa no existe')
            response = {'msg': 'Categoria No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def delete(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            categoria = Categoria.objects.get(id=id)
            categoria.delete()
            response = {'msg': 'Categoria Eliminada Correctamente'} # con este estatus 204 no se devuelve el response
        except Categoria.DoesNotExist:
            print('La Categoria no existe')
            response = {'msg': 'Categoria No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


# ========== CLIENTES ========== |
class ClienteListCreateAPIView(PaginationMixins, APIView):
    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK

        clientes = Cliente.objects.all()

        orden = request.GET.get('orden')
        rango_fecha = request.GET.get('rango_fecha')
        q = request.GET.get('q')

        if q:
            clientes = clientes.filter(
                Q(id__icontains=q) |
                Q(nombre__icontains=q) |
                Q(primer_apellido__icontains=q) |
                Q(segundo_apellido__icontains=q) |
                Q(rut__icontains=q)
            )
        if orden:
            if orden == 'asc':
                clientes = clientes.order_by('created')
            else:
                clientes = clientes.order_by('-created')

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            clientes = clientes.filter(created__range=[fechas[0], fechas[1]])

        try:
            # Obtener la página actual
            page = self.paginate_queryset(clientes, request)
            if page is not None:
                # Serializer tus datos como de costumbre
                serializer = ClienteSerializer(page, many=True)
                
                # Devolver los datos paginados junto con los metadatos
                response = self.get_paginated_response(serializer.data)

        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        try:
            serializer = ClienteSerializer(data=request.data)
            if serializer.is_valid():
                cliente = serializer.save()
                print(ClienteSerializer(cliente).data)
                response = ClienteSerializer(cliente).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


class ClienteRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, APIView):
    # list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            cliente = Cliente.objects.get(id=id)
            serializer = ClienteSerializer(cliente)
            response = serializer.data
        except Cliente.DoesNotExist:
            print('La Cliente no existe')
            response = {'msg': 'Cliente No Encontrado'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def put(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            cliente = Cliente.objects.get(pk=id)
            serializer = ClienteSerializer(data=request.data, instance=cliente)
            if serializer.is_valid():
                cliente = serializer.save()
                response = ClienteSerializer(cliente).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Cliente.DoesNotExist:
            print('La Cliente no existe')
            response = {'msg': 'Cliente No Encontrado'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def delete(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            cliente = Cliente.objects.get(id=id)
            cliente.delete()
            response = {'msg': 'Cliente Eliminado Correctamente'} # con este estatus 204 no se devuelve el response
        except Cliente.DoesNotExist:
            print('La Cliente no existe')
            response = {'msg': 'Cliente No Encontrado'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


# ========== ESPECIALIDADES ========== |
class EspecialidadListCreateAPIView(PaginationMixins, APIView):
    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK

        especialidades = Especialidad.objects.all()

        orden = request.GET.get('orden')
        rango_fecha = request.GET.get('rango_fecha')
        q = request.GET.get('q')

        if q:
            especialidades = especialidades.filter(
                Q(id__icontains=q) |
                Q(nombre__icontains=q)
            )
        if orden:
            if orden == 'asc':
                especialidades = especialidades.order_by('created')
            else:
                especialidades = especialidades.order_by('-created')

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            especialidades = especialidades.filter(created__range=[fechas[0], fechas[1]])

        try:
            # Obtener la página actual
            page = self.paginate_queryset(especialidades, request)
            if page is not None:
                # Serializer tus datos como de costumbre
                serializer = EspecialidadSerializer(page, many=True)
                
                # Devolver los datos paginados junto con los metadatos
                response = self.get_paginated_response(serializer.data)

        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        try:
            serializer = EspecialidadSerializer(data=request.data)
            if serializer.is_valid():
                especialidad = serializer.save()
                print(EspecialidadSerializer(especialidad).data)
                response = EspecialidadSerializer(especialidad).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


class EspecialidadRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, APIView):
    # list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            especialidad = Especialidad.objects.get(id=id)
            serializer = EspecialidadSerializer(especialidad)
            response = serializer.data
        except Especialidad.DoesNotExist:
            print('La Especialidad no existe')
            response = {'msg': 'Especialidad No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def put(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            especialidad = Especialidad.objects.get(pk=id)
            serializer = EspecialidadSerializer(data=request.data, instance=especialidad)
            if serializer.is_valid():
                especialidad = serializer.save()
                response = EspecialidadSerializer(especialidad).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Especialidad.DoesNotExist:
            print('La Especialidad no existe')
            response = {'msg': 'Especialidad No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def delete(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            especialidad = Especialidad.objects.get(id=id)
            especialidad.delete()
            response = {'msg': 'Especialidad Eliminada Correctamente'} # con este estatus 204 no se devuelve el response
        except Especialidad.DoesNotExist:
            print('La Especialidad no existe')
            response = {'msg': 'Especialidad No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


# ========== HORARIOS ========== |
class HorarioListCreateAPIView(PaginationMixins, APIView):
    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK

        horarios = Horario.objects.all()

        orden = request.GET.get('orden')
        rango_fecha = request.GET.get('rango_fecha')
        q = request.GET.get('q')

        if q:
            horarios = horarios.filter(
                Q(id__icontains=q) |
                Q(dia__icontains=q) |
                Q(especialista__user__username__icontains=q)
            )
        if orden:
            if orden == 'asc':
                horarios = horarios.order_by('created')
            else:
                horarios = horarios.order_by('-created')

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            horarios = horarios.filter(created__range=[fechas[0], fechas[1]])

        # Obtener horarios por dia y especialista
        fecha = None
        DIAS_SEMANA = {
            '0': 'LU',
            '1': 'MA',
            '2': 'MI',
            '3': 'JU',
            '4': 'VI',
            '5': 'SA',
            '6': 'DO'
        }

        especialista = request.GET.get('especialista')
        fecha_str = request.GET.get('fecha')

        if especialista:
            especialista = EspecialistaProfile.objects.get(pk=especialista)
            horarios = horarios.filter(especialista=especialista)

        if fecha_str:
            # Convertimos la cadena a un objeto date y obtenemos el dia de la semana
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            dia_semana = DIAS_SEMANA[str(fecha.weekday())]
            horarios = horarios.filter(dia=dia_semana)
            # # Validar la fecha de término del contrato del especialista
            if fecha and especialista and fecha > especialista.termino_contrato:
                horarios = []

        try:
            # Obtener la página actual
            page = self.paginate_queryset(horarios, request)
            if page is not None:
                # Serializer tus datos como de costumbre
                serializer = HorarioSerializer(page, many=True)

                # Devolver los datos paginados junto con los metadatos
                response = self.get_paginated_response(serializer.data)

        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        try:
            serializer = HorarioSerializer(data=request.data)
            if serializer.is_valid():
                horario = serializer.save()
                print(HorarioSerializer(horario).data)
                response = HorarioSerializer(horario).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


class HorarioRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, APIView):
    # list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            horario = Horario.objects.get(id=id)
            serializer = HorarioSerializer(horario)
            response = serializer.data
        except Horario.DoesNotExist:
            print('La Horario no existe')
            response = {'msg': 'Horario No Encontrado'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def put(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            horario = Horario.objects.get(pk=id)
            serializer = HorarioSerializer(data=request.data, instance=horario)
            if serializer.is_valid():
                horario = serializer.save()
                response = HorarioSerializer(horario).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Horario.DoesNotExist:
            print('La Horario no existe')
            response = {'msg': 'Horario No Encontrado'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def delete(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            horario = Horario.objects.get(id=id)
            horario.delete()
            response = {'msg': 'Horario Eliminado Correctamente'} # con este estatus 204 no se devuelve el response
        except Horario.DoesNotExist:
            print('La Horario no existe')
            response = {'msg': 'Horario No Encontrado'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


# ========== PAGOS ========== |
class PagoListCreateAPIView(PaginationMixins, APIView):
    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK

        pagos = Pago.objects.all()
        
        metodo = request.GET.get('metodo')   
        orden = request.GET.get('orden')
        rango_fecha = request.GET.get('rango_fecha')
        q = request.GET.get('q')

        if q:
            pagos = pagos.filter(
                Q(id__icontains=q) |
                Q(cita__id__icontains=q) |
                Q(cita__cliente__nombre__icontains=q) |
                Q(cita__cliente__rut__icontains=q) |
                Q(cod_especialista__icontains=q) |
                Q(folio__icontains=q)
            )
        if orden:
            if orden == 'asc':
                pagos = pagos.order_by('created')
            else:
                pagos = pagos.order_by('-created')

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            pagos = pagos.filter(created__range=[fechas[0], fechas[1]])

        if metodo:
            pagos = pagos.filter(metodo__in=metodo.split(','))

        try:
            # page_obj = self.paginate_queryset(tarifas, request)
            # serializer = TarifaSerializer(page_obj, many=True)
            # if serializer.data:
            #     print(self.get_paginated_response(serializer.data))
            #     print(type(self.get_paginated_response(serializer.data)))
            #     response['data'] = serializer.data
            #     response['paginator'] = self.get_paginated_response(serializer.data)
            # else:
            #     response['data'] = {'detail': "Not content"}

            # Obtener la página actual
            page = self.paginate_queryset(pagos, request)
            if page is not None:
                # Serializer tus datos como de costumbre
                serializer = PagoSerializer(page, many=True)
                
                # Devolver los datos paginados junto con los metadatos
                response = self.get_paginated_response(serializer.data)

        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        try:
            serializer = PagoSerializer(data=request.data, context=request.data)
            if serializer.is_valid():
                pago = serializer.save()
                print(PagoSerializer(pago).data)
                response = PagoSerializer(pago).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


class PagoRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, APIView):
    # list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            pago = Pago.objects.get(id=id)
            serializer = PagoSerializer(pago)
            response = serializer.data
        except Pago.DoesNotExist:
            print('El Pago no existe')
            response = {'msg': 'Pago No Encontrado'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def put(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            pago = Pago.objects.get(pk=id)
            serializer = PagoSerializer(data=request.data, instance=pago)
            if serializer.is_valid():
                pago = serializer.save()
                response = PagoSerializer(pago).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Pago.DoesNotExist:
            print('El Pago no existe')
            response = {'msg': 'Pago No Encontrado'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def delete(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            pago = Pago.objects.get(id=id)
            pago.delete()
            response = {'msg': 'Pago Eliminado Correctamente'} # con este estatus 204 no se devuelve el response
        except Pago.DoesNotExist:
            print('El Pago no existe')
            response = {'msg': 'Pago No Encontrado'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


# ========== CITAS ========== |
class CitaListCreateAPIView(PaginationMixins, APIView):
    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK

        citas = Cita.objects.all()
  
        estado = request.GET.get('estado')
        realizada = request.GET.get('realizada')
        rut = request.GET.get('rut')
        orden = request.GET.get('orden')
        rango_fecha = request.GET.get('rango_fecha')
        especialista = request.GET.get('especialista')
        q = request.GET.get('q')

        if q:
            citas = citas.filter(
                Q(id__icontains=q) |
                Q(cliente__nombre__icontains=q) |
                Q(cliente__rut__icontains=q) |
                Q(especialista__user__username__icontains=q) |
                Q(especialidad__icontains=q)
            )
        if orden:
            if orden == 'asc':
                citas = citas.order_by('created')
            else:
                citas = citas.order_by('-created')

        if rut:
            citas = citas.filter(cliente__rut=rut.lower(),
                                 estado='RS')
        if estado:
            citas = citas.filter(estado__in=estado.split(','))
        if realizada:
            if 'T' in realizada and 'F' in realizada:
                citas = citas
            elif 'T' in realizada:
                citas = citas.filter(realizada=True)
            elif 'F' in realizada:
                citas = citas.filter(realizada=False)
        if especialista:
            citas = citas.filter(especialista__pk=especialista)

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            citas = citas.filter(fecha__range=[fechas[0], fechas[1]])
        try:
            # page_obj = self.paginate_queryset(tarifas, request)
            # serializer = TarifaSerializer(page_obj, many=True)
            # if serializer.data:
            #     print(self.get_paginated_response(serializer.data))
            #     print(type(self.get_paginated_response(serializer.data)))
            #     response['data'] = serializer.data
            #     response['paginator'] = self.get_paginated_response(serializer.data)
            # else:
            #     response['data'] = {'detail': "Not content"}

            # Obtener la página actual
            page = self.paginate_queryset(citas, request)
            if page is not None:
                # Serializer tus datos como de costumbre
                serializer = CitaCreateSerializer(page, many=True)
                
                # Devolver los datos paginados junto con los metadatos
                response = self.get_paginated_response(serializer.data)

        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        try:
            serializer = CitaCreateSerializer(data=request.data, context=request.data)
            if serializer.is_valid():
                cita = serializer.save()
                print(CitaCreateSerializer(cita).data)
                response = CitaCreateSerializer(cita).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


class CitaRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, APIView):
    # list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            cita = Cita.objects.get(id=id)
            serializer = CitaCreateSerializer(cita)
            response = serializer.data
        except Cita.DoesNotExist:
            print('El Cita no existe')
            response = {'msg': 'Cita No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def put(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            cita = Cita.objects.get(pk=id)
            serializer = CitaCreateSerializer(data=request.data, instance=cita)
            if serializer.is_valid():
                cita = serializer.save()
                response = CitaCreateSerializer(cita).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Cita.DoesNotExist:
            print('El Cita no existe')
            response = {'msg': 'Cita No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)

    def delete(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        id = self.kwargs['id']
        try:
            cita = Cita.objects.get(id=id)
            cita.delete()
            response = {'msg': 'Cita Eliminada Correctamente'} # con este estatus 204 no se devuelve el response
        except Cita.DoesNotExist:
            print('El Cita no existe')
            response = {'msg': 'Cita No Encontrada'}
            status_res = status.HTTP_404_NOT_FOUND
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


# ========== HISTORIAL ANULACIONES ========== |
class HistorialAnulacionListCreateAPIView(PaginationMixins, APIView):

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        try:
            serializer = HistorialAnulacionSerializer(data=request.data, context=request.data)
            if serializer.is_valid():
                categoria = serializer.save()
                print(HistorialAnulacionSerializer(categoria).data)
                response = HistorialAnulacionSerializer(categoria).data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


# ========== ESPECIALISTAS ========== |
class EspecialistaListCreateAPIView(PaginationMixins, APIView):
    def get(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK

        especialistas = Especialista.objects.all()

        orden = request.GET.get('orden')
        rango_fecha = request.GET.get('rango_fecha')
        q = request.GET.get('q')

        if q:
            especialistas = especialistas.filter(
                Q(id__icontains=q) |
                Q(nombre__icontains=q)
            )
        if orden:
            if orden == 'asc':
                especialistas = especialistas.order_by('created')
            else:
                especialistas = especialistas.order_by('-created')

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            especialistas = especialistas.filter(created__range=[fechas[0], fechas[1]])

        try:
            # Obtener la página actual
            page = self.paginate_queryset(especialistas, request)
            if page is not None:
                # Serializer tus datos como de costumbre
                serializer = EspecialistaCreateSerializer(page, many=True)
              
                # Devolver los datos paginados junto con los metadatos
                response = self.get_paginated_response(serializer.data)

        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response, status=status_res)

    def post(self, request, *args, **kwargs):
        status_res = status.HTTP_200_OK
        try:
            serializer = EspecialistaCreateSerializer(data=request.data, context=request.data)
            if serializer.is_valid():
                serializer.save()
                response = serializer.data
            else:
                print(serializer.errors)
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                print(error_messages)
                response = {"msg": error_messages}
                status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)