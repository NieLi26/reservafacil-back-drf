import json
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from datetime import date, datetime, timedelta
from django.db.models import Q  # Global search
from django.views.generic import View

from rest_framework.views import APIView
from rest_framework.response import Response
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
from apps.booking.forms import (
    ClienteForm, CitaCreateForm,
    PagoForm, HistorialAnulacionForm,
    CategoriaForm, EspecialidadForm,
    TarifaForm, HorarioForm, CitaRealizadaForm
)
from apps.booking.serializers import (
    TarifaSerializer
)

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
            serializer = TarifaSerializer(data=request.data)
            if serializer.is_valid():
                tarifa = serializer.save()
                print(TarifaSerializer(tarifa).data)
                response = TarifaSerializer(tarifa).data
            else:
                print(serializer.errors)
                response = {"msg": 'Error en los datos'}
                status_res = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(str(e))
            response = {"msg": 'Error inesperado, Intente mas tarde'}
            status_res = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JsonResponse(response, status=status_res)


class TarifaRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, View):
    list_methods = ['PUT', 'DELETE']
    
    def get(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            id = self.kwargs['id']
            tarifa = Tarifa.objects.get(id=id)
            response['data'] = tarifa.get_data()
            status = 200
        except Tarifa.DoesNotExist:
            print('La Tarifa no existe')
            response['error'] = 'La Tarifa no Existe'
            status = 404
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

    def put(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            data = json.loads(request.body)
            id = self.kwargs['id']
            tarifa = Tarifa.objects.get(id=id)
            form = TarifaForm(data, instance=tarifa)
            if form.is_valid():
                form.save()
                response['success'] = 'Tarifa Guardada Correctamente'
                status = 200
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Tarifa.DoesNotExist:
            print('La Tarifa no existe')
            response['error'] = 'La Tarifa no Existe'
            status = 404
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

    def delete(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            tarifa_id = self.kwargs['id']
            tarifa = Tarifa.objects.get(id=tarifa_id)
            tarifa.delete()
            response['success'] = 'Tarifa Eliminada Correctamente'  # con este estatus 204 no se devuelve el response
            status = 204
        except Tarifa.DoesNotExist:
            print('La Tarifa no existe')
            response['error'] = 'La Tarifa no Existe'
            status = 404
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

