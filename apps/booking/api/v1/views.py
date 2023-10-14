import json
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from datetime import date, datetime, timedelta
from django.db.models import Q  # Global search
from django.views.generic import View

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
from apps.accounts.models import EspecialistaProfile


def categoria_json(request):
    # categorias = Categoria.objects.all()
    # data = [categoria.get_data() for categoria in categorias]
    data = list(Categoria.objects.values())
    response = {
        'data': data
    }
    return JsonResponse(response)


def especialidad_json(request, id=None):
    response = {}
    if id:
        try:
            especialidad = Especialidad.objects.get(pk=id)
            response['data'] = especialidad.get_data()
        except Especialidad.DoesNotExist:
            print('esta especialidad no existe')
            response['error'] = 'Esta Especialidad no Existe'
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
    else:
        categoria = request.GET.get('categoria')
        especialidades = Especialidad.objects.all()
        if categoria:
            especialidades = especialidades.filter(categoria=categoria)

        response['data'] = [especialidad.get_data() for especialidad in especialidades]
        # response['data'] = list(especialidades.values())
    return JsonResponse(response)


def especialista_json(request, id=None):
    response = {}
    if id:
        try:
            especialista = EspecialistaProfile.objects.get(pk=id)
            response['data'] = especialista.get_data()
        except EspecialistaProfile.DoesNotExist:
            print('este especialista no existe')
            response['error'] = 'Este Especialista no Existe'
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
    else:
        especialistas = EspecialistaProfile.objects.all()

        especialidad = request.GET.get('especialidad')
        especialista = request.GET.get('especialista')
        nombre = request.GET.get('nombre')
        print(especialidad)
        if nombre:
            especialistas = especialistas.filter(user__username__icontains=nombre)
        if especialidad:
            especialistas = especialistas.filter(especialidades__pk=especialidad)
        if especialista:
            especialistas = especialistas.filter(pk=especialista)

        response['data'] = [especialista.get_data() for especialista in especialistas]
        # response['data'] = list(especialidades.values())
    return JsonResponse(response)


def horario_json(request):
    response = {}
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
    try:
        horarios = Horario.objects.all()
        especialista = request.GET.get('especialista')
        fecha_str = request.GET.get('fecha')
        # if especialista and fecha_str:
        #     # Convertimos la cadena a un objeto date y obtenemos el dia de la semana
        #     fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        #     dia_semana = DIAS_SEMANA[str(fecha.weekday())]
        #     especialista = EspecialistaProfile.objects.get(pk=especialista)

        #     horario = Horario.objects.get(especialista=especialista,
        #                                   dia=dia_semana).get_data(fecha)
        #     response['data'] = horario
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
        # Hacemos esto para doblar la validacion, y no mostrar horarios al seleccioanr fecha(que nose deberia con la validacion de abajo)
        # Ademas por seguridad mandamos la fecha de termino contrato, para deshabilitar los dias posteriores
        response['data'] = {
            'fecha_limite': especialista.termino_contrato,
            'horarios': [horario.get_data(fecha) for horario in horarios]
        }
    except Horario.DoesNotExist:
        print('este horario no existe')
        response['error'] = 'Este horario no Existe'
    return JsonResponse(response)


# ========== CITAS ========== |
class CitaListCreateAPIView(PaginationMixin, View):
    def get(self, request, *args, **kwargs):
        response = {}
        status = None

        citas = Cita.objects.all()
        # autenticacion solucion parche, porque usare un mixin
        if request.user.is_authenticated and request.user.tipo == 'ESP':
            citas = citas.filter(especialista__user=request.user)

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
                citas = citas.order_by('cliente__nombre')
            else:
                citas = citas.order_by('-cliente__nombre')
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

        page_number = request.GET.get('page', 1)
        try:
            paginated_data = self.paginate_queryset(citas, page_number)

            response['data'] = [page.get_data() for page in paginated_data['page_obj']]
            response['paginator'] = paginated_data['paginator']
            status = 200
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

    def post(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            cliente_form = ClienteForm(request.POST)
            cita_form = CitaCreateForm(request.POST)

            rut = request.POST.get('rut').lower()
            cliente_exist = Cliente.objects.filter(rut=rut)
            if cliente_exist.exists():
                cliente_form = ClienteForm(request.POST,
                                           instance=cliente_exist.first())

            if cita_form.is_valid() and cliente_form.is_valid():
                cliente = cliente_form.save()
                cita = cita_form.save(commit=False)

                # Realizar la validación de total_citas aquí antes de guardar la cita
                fecha = cita.fecha

                if validar_citas_cliente_fecha(cliente, fecha):
                    response['error'] = 'No puede Reservar más de 3 Citas el mismo Día.'
                    status = 403
                else:
                    cita.cliente = cliente
                    cita.save()
                    response['success'] = {'message': 'Cita Guardada Correctamente',
                                           'cita': cita.id}
                    status = 200
            else:
                print(cita_form.errors)
                print(cliente_form.errors)
                # response['error'] = 'No se Pudo Guardar su Cuta, Intente Nuevamente'
                response['error_form'] = {
                    'cita_form': cita_form.errors,
                    'cliente_form': cliente_form.errors
                }
                status = 422
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


class CitaRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, View):
    list_methods = ['DELETE']

    def get(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            cita_id = self.kwargs['id']
            cita = Cita.objects.get(id=cita_id)
            response['data'] = cita.get_data()
            status = 200
        except Cita.DoesNotExist:
            print('La Cita no existe')
            response['error'] = 'La Cita no Existe'
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
            action = data['action']

            cita_id = self.kwargs['id']
            cita = Cita.objects.get(id=cita_id)

            if action == 'anular':
                if not self.is_allowed(request, 'Administrador'):
                    status = 403
                    response['error'] = 'No tiene permiso para  realizar esta accion'
                    return JsonResponse(response, status=status) 

                historial_data = {
                    'cita': cita,
                    'motivo': data['motivo']
                }
                form = HistorialAnulacionForm(historial_data)
                if form.is_valid():
                    cita.estado = 'AN'
                    cita.save()
                    form.save()
                    response['success'] = {
                        'message': 'Cita anulada correctamente',
                        'rut': cita.cliente.rut
                    }
                    status = 200
                else:
                    print(form.errors)
                    response['error_form'] = form.errors
                    status = 422
            elif action == 'anular_general':
                historial_data = {
                    'cita': cita,
                    'motivo': 'Anulado por Cliente'
                }
                form = HistorialAnulacionForm(historial_data)
                if form.is_valid():
                    cita.estado = 'AN'
                    cita.save()
                    form.save()
                    # motivo = data['data']['motivo']
                    # HistorialAnulacion.objects.create(cita=cita, motivo=motivo)
                    response['success'] = {
                        'message': 'Cita anulada correctamente',
                        'rut': cita.cliente.rut
                    }
                    status = 200
                else:
                    print(form.errors)
                    response['error_form'] = form.errors
                    status = 422
            elif action == 'confirmar_general':
                # Restringir reservar con 12 horas de anticipacion
                fecha_actual = datetime.now()
                fecha_reserva = datetime.combine(cita.fecha, cita.hora)

                # Calcular la diferencia de tiempo entre la fecha de reserva y la actual
                tiempo_anticipacion = fecha_reserva - fecha_actual

                # Verificar si se cumplen las 12 horas de anticipación para reservar
                if tiempo_anticipacion < timedelta(hours=12):
                    response['error'] = 'Debes confirmar con al menos 12 horas de anticipación.'
                    status = 403
                else:
                    cita.estado = 'CF'
                    cita.save()
                    response['success'] = {
                        'message': 'Cita confirmada correctamente',
                        'rut': cita.cliente.rut
                    }
                    status = 200
            elif action == 'realizar':
                if not self.is_allowed(request, 'Especialista'):
                    status = 403
                    response['error'] = 'No tiene permiso para  realizar esta accion'
                    return JsonResponse(response, status=status)

                form = CitaRealizadaForm(data)
                if form.is_valid():
                    obs = form.cleaned_data['obs']
                    if validar_cita_confirmada(cita_id):
                        cita.realizada = True
                        cita.obs = obs
                        cita.save()
                        response['success'] = {
                            'message': 'Cita Realizada correctamente',
                            'rut': cita.cliente.rut
                        }
                        status = 200
                    else:
                        response['error'] = 'Solo puede Realizar una Cita Confirmada'
                        status = 403
                else:
                    print(form.errors)
                    response['error_form'] = form.errors
                    status = 422
            else:
                response['error'] = 'La Acción no es Valida'
                status = 403
        except Cita.DoesNotExist:
            print('La Cita no existe')
            response['error'] = 'La Cita no Existe'
            status = 404
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


# ========== CLIENTES ========== |
class ClienteListCreateAPIView(PaginationMixin, View):
    def get(self, request, *args, **kwargs):
        response = {}
        status = None

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
                clientes = clientes.order_by('nombre')
            else:
                clientes = clientes.order_by('-nombre')

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            clientes = clientes.filter(created__range=[fechas[0], fechas[1]])

        page_number = request.GET.get('page', 1)
        try:
            paginated_data = self.paginate_queryset(clientes, page_number)

            response['data'] = [page.get_data() for page in paginated_data['page_obj']]
            response['paginator'] = paginated_data['paginator']
            status = 200
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

    def post(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            form = ClienteForm(request.POST)
            if form.is_valid():
                form.save()
                response['success'] = 'Cliente Guardado Correctamente'
                status = 200
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


class ClienteRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, View):
    list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            cliente_rut = self.kwargs['rut']
            print(cliente_rut)
            cliente = Cliente.objects.get(rut=cliente_rut)
            response['data'] = cliente.get_data()
            status = 200
        except Cliente.DoesNotExist:
            print('El Cliente no existe')
            response['error'] = 'El Cliente no Existe'
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
            cliente_rut = self.kwargs['rut']
            cliente = Cliente.objects.get(rut=cliente_rut)
            form = ClienteForm(data, instance=cliente)
            if form.is_valid():
                form.save()
                response['success'] = 'Cliente Guardado Correctamente'
                status = 200
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Cliente.DoesNotExist:
            print('El Cliente no existe')
            response['error'] = 'El Cliente no Existe'
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

    def delete(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            cliente_rut = self.kwargs['rut']
            cliente = Cliente.objects.get(rut=cliente_rut)
            cliente.delete()
            response['success'] = 'Cliente Eliminado Correctamente'  # con este estatus 204 no se devuelve el response
            status = 204
        except Cliente.DoesNotExist:
            print('El Cliente no existe')
            response['error'] = 'El Cliente no Existe'
            status = 404
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


# ========== PAGOS ========== |
class PagoListCreateAPIView(PaginationMixin, View):
    def get(self, request, *args, **kwargs):
        response = {}
        status = None

        pagos = Pago.objects.all()

        metodo = request.GET.get('metodo')
        # rut = request.GET.get('rut')
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
                pagos = pagos.order_by('cliente__nombre')
            else:
                pagos = pagos.order_by('-cliente__nombre')
        # if rut:
        #     citas = citas.filter(cliente__rut=rut.lower(),
        #                          estado='RS')
        if metodo:
            pagos = pagos.filter(metodo__in=metodo.split(','))
            
        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            pagos = pagos.filter(created__range=[fechas[0], fechas[1]])

        page_number = request.GET.get('page', 1)
        try:
            paginated_data = self.paginate_queryset(pagos, page_number)

            response['data'] = [page.get_data() for page in paginated_data['page_obj']]
            response['paginator'] = paginated_data['paginator']
            status = 200
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

    def post(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            form = PagoForm(request.POST)
            print(request.POST.get('folio'))
            if form.is_valid():
                instance = form.save(commit=False)
                print(instance.cita)
                if validar_cita_confirmada(instance.cita.id):
                    instance.save()
                    response['success'] = 'Pago Guardado Correctamente'
                    status = 200
                else:
                    response['error'] = 'Solo puede Pagar una Cita Confirmada'
                    status = 403
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


# ========== CATEGORIAS ========== |
class CategoriaListCreateAPIView(PaginationMixin, View):
    def get(self, request, *args, **kwargs):
        response = {}
        status = None

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

        page_number = request.GET.get('page', 1)
        try:
            paginated_data = self.paginate_queryset(categorias, page_number)

            response['data'] = [page.get_data() for page in paginated_data['page_obj']]
            response['paginator'] = paginated_data['paginator']
            status = 200
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

    def post(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            form = CategoriaForm(request.POST)
            if form.is_valid():
                form.save()
                response['success'] = 'Categoria Guardada Correctamente'
                status = 200
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


class CategoriaRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, View):
    list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            id = self.kwargs['id']
            categoria = Categoria.objects.get(id=id)
            response['data'] = categoria.get_data()
            status = 200
        except Categoria.DoesNotExist:
            print('La Categoria no existe')
            response['error'] = 'La Categoria no Existe'
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
            categoria_id = self.kwargs['id']
            categoria = Categoria.objects.get(id=categoria_id)
            form = CategoriaForm(data, instance=categoria)
            if form.is_valid():
                form.save()
                response['success'] = 'Categoria Guardada Correctamente'
                status = 200
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Categoria.DoesNotExist:
            print('La Categoria no existe')
            response['error'] = 'La Categoria no Existe'
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
            categoria_id = self.kwargs['id']
            categoria = Categoria.objects.get(id=categoria_id)
            categoria.delete()
            response['success'] = 'Categoria Eliminada Correctamente'  # con este estatus 204 no se devuelve el response
            status = 204
        except Categoria.DoesNotExist:
            print('La Categoria no existe')
            response['error'] = 'La Categoria no Existe'
            status = 404
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


# ========== ESPECIALIDADES ========== |

class EspecialidadListCreateAPIView(PaginationMixin, View):
    def get(self, request, *args, **kwargs):
        response = {}
        status = None

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

        # Filtros especificos
        categoria = request.GET.get('categoria')
        if categoria:
            especialidades = especialidades.filter(categoria=categoria)

        # Comprobar sino se desea paginacion
        paginate = request.GET.get('paginate', 'yes')

        if paginate == 'no':
            try:
                response['data'] = [especialidad.get_data() for especialidad in especialidades]
                status = 200
            except Exception as e:
                print(str(e))
                response['error'] = 'Error inesperado, Intente mas tarde'
                status = 500
        else:
            page_number = request.GET.get('page', 1)
            try:
                paginated_data = self.paginate_queryset(especialidades, page_number)

                response['data'] = [page.get_data() for page in paginated_data['page_obj']]
                response['paginator'] = paginated_data['paginator']
                status = 200
            except Exception as e:
                print(str(e))
                response['error'] = 'Error inesperado, Intente mas tarde'
                status = 500
        return JsonResponse(response, status=status)

    def post(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            form = EspecialidadForm(request.POST)
            if form.is_valid():
                form.save()
                response['success'] = 'Especialidad Guardada Correctamente'
                status = 200
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


class EspecialidadRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, View):
    list_methods = ['PUT', 'DELETE']
    
    def get(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            id = self.kwargs['id']
            especialidad = Especialidad.objects.get(id=id)
            response['data'] = especialidad.get_data()
            status = 200
        except Especialidad.DoesNotExist:
            print('La Especialidad no existe')
            response['error'] = 'La Especialidad no Existe'
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
            especialidad = Especialidad.objects.get(id=id)
            form = EspecialidadForm(data, instance=especialidad)
            if form.is_valid():
                form.save()
                response['success'] = 'Especialidad Guardada Correctamente'
                status = 200
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Especialidad.DoesNotExist:
            print('La Especialidad no existe')
            response['error'] = 'La Categoria no Existe'
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
            especialidad_id = self.kwargs['id']
            especialidad = Especialidad.objects.get(id=especialidad_id)
            especialidad.delete()
            response['success'] = 'Especialidad Eliminada Correctamente'  # con este estatus 204 no se devuelve el response
            status = 204
        except Especialidad.DoesNotExist:
            print('La Especialidad no existe')
            response['error'] = 'La Especialidad no Existe'
            status = 404
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


# ========== TARIFAS ========== |
class TarifaListCreateAPIView(PaginationMixin, View):
    def get(self, request, *args, **kwargs):
        response = {}
        status = None

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

        page_number = request.GET.get('page', 1)
        try:
            paginated_data = self.paginate_queryset(tarifas, page_number)

            response['data'] = [page.get_data() for page in paginated_data['page_obj']]
            response['paginator'] = paginated_data['paginator']
            status = 200
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

    def post(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            form = TarifaForm(request.POST)
            if form.is_valid():
                form.save()
                response['success'] = 'Tarifa Guardada Correctamente'
                status = 200
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


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


# ========== HORARIOS ========== |
class HorarioListCreateAPIView(PaginationMixin, View):
    def get(self, request, *args, **kwargs):
        response = {}
        status = None

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
                horarios = horarios.order_by('duracion')
            else:
                horarios = horarios.order_by('-duracion')

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

        page_number = request.GET.get('page', 1)
        try:
            paginated_data = self.paginate_queryset(horarios, page_number)

            response['data'] = [page.get_data(fecha) for page in paginated_data['page_obj']]
            response['paginator'] = paginated_data['paginator']
            status = 200
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

    def post(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            form = HorarioForm(request.POST)
            if form.is_valid():
                form.save()
                response['success'] = 'Horario Guardado Correctamente'
                status = 200
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


class HorarioRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, View):
    list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            horario_id = self.kwargs['id']
            horario = Horario.objects.get(id=horario_id)
            response['data'] = horario.get_data()
            status = 200
        except Horario.DoesNotExist:
            print('El Horario no existe')
            response['error'] = 'El Horario no Existe'
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
            horario_id = self.kwargs['id']
            horario = Horario.objects.get(id=horario_id)
            form = HorarioForm(data, instance=horario)
            if form.is_valid():
                form.save()
                response['success'] = 'Horario Guardado Correctamente'
                status = 200
            else:
                print(form.errors)
                response['error_form'] = form.errors
                status = 422
        except Horario.DoesNotExist:
            print('El Horario no existe')
            response['error'] = 'El Horario no Existe'
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
            horario_id = self.kwargs['id']
            horario = Horario.objects.get(id=horario_id)
            horario.delete()
            response['success'] = 'Horario Eliminado Correctamente'  # con este estatus 204 no se devuelve el response
            status = 204
        except Horario.DoesNotExist:
            print('El Horario no existe')
            response['error'] = 'El Horario no Existe'
            status = 404
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


# ========== ESPECIALISTAS ========== |
class EspecialistaListCreateAPIView(PaginationMixin, View):
    def get(self, request, *args, **kwargs):
        response = {}
        status = None

        especialistas = EspecialistaProfile.objects.all()

        nombre = request.GET.get('nombre')
        orden = request.GET.get('orden')
        rango_fecha = request.GET.get('rango_fecha')
        q = request.GET.get('q')

        if q:
            especialistas = especialistas.filter(
                Q(id__icontains=q) |
                Q(especialidades__nombre__icontains=q) |
                Q(user__username__icontains=q)
            )
        if orden:
            if orden == 'asc':
                especialistas = especialistas.order_by('created')
            else:
                especialistas = especialistas.order_by('-created')

        if rango_fecha:
            fechas = rango_fecha.split(' a ')
            especialistas = especialistas.filter(created__range=[fechas[0], fechas[1]])

        if nombre:
            especialistas = especialistas.filter(user__username__icontains=nombre)

        # Filtros especificos
        especialidad = request.GET.get('especialidad')
        if especialidad:
            print(especialidad)
            especialistas = especialistas.filter(especialidades__id=especialidad)

        # Comprobar sino se desea paginacion
        paginate = request.GET.get('paginate', 'yes')

        if paginate == 'no':
            try:
                response['data'] = [especialista.get_data() for especialista in especialistas]
                status = 200
            except Exception as e:
                print(str(e))
                response['error'] = 'Error inesperado, Intente mas tarde'
                status = 500
        else:
            page_number = request.GET.get('page', 1)
            try:
                paginated_data = self.paginate_queryset(especialistas, page_number)

                response['data'] = [page.get_data() for page in paginated_data['page_obj']]
                response['paginator'] = paginated_data['paginator']
                status = 200
            except Exception as e:
                print(str(e))
                response['error'] = 'Error inesperado, Intente mas tarde'
                status = 500
        return JsonResponse(response, status=status)

    def post(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            profile_form = EspecialistaProfileForm(request.POST)
            especialista_form = EspecialistaCreationForm(request.POST)
            print(request.POST.get('email'))
            if especialista_form.is_valid() and profile_form.is_valid():
                especialista = especialista_form.save()
                profile = profile_form.save(commit=False)
                profile.user = especialista
                profile.save()
                response['success'] = 'Especialista Guardado Correctamente'
                status = 200
            else:
                print(profile_form.errors)
                print(especialista_form.errors)
                response['error_form'] = {
                    'profile_form': profile_form.errors,
                    'especialista_form': especialista_form.errors
                }
                status = 422
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)


class EspecialistaRetrieveUpdateDestroyAPIView(CustomUserPassesTestMixin, View):
    list_methods = ['PUT', 'DELETE']

    def get(self, request, *args, **kwargs):
        response = {}
        status = None
        try:
            especialista_id = self.kwargs['id']
            especialista = EspecialistaProfile.objects.get(id=especialista_id)
            response['data'] = especialista.get_data()
            status = 200
        except EspecialistaProfile.DoesNotExist:
            print('La Especialista no existe')
            response['error'] = 'El Especialista no Existe'
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
            especialista_id = self.kwargs['id']
            especialista = EspecialistaProfile.objects.get(id=especialista_id)

            profile_form = EspecialistaProfileForm(data, instance=especialista)
            especialista_form = EspecialistaChangeForm(data, instance=especialista.user)
            if especialista_form.is_valid() and profile_form.is_valid():
                especialista_form.save()
                profile_form.save()
                response['success'] = 'Especialista Actualizado Correctamente'
                status = 200
            else:
                print(profile_form.errors)
                print(especialista_form.errors)
                response['error_form'] = {
                    'profile_form': profile_form.errors,
                    'especialista_form': especialista_form.errors
                }
                status = 422
        except EspecialistaProfile.DoesNotExist:
            print('El Especialista no existe')
            response['error'] = 'El Especialista no Existe'
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
            especialista_id = self.kwargs['id']
            especialista = EspecialistaProfile.objects.get(id=especialista_id)
            custom_user = get_user_model().objects.get(pk=especialista.user.id)
            custom_user.delete()
            response['success'] = 'Especialista Eliminado Correctamente'  # con este estatus 204 no se devuelve el response
            status = 204
        except EspecialistaProfile.DoesNotExist:
            print('El Especialista no existe')
            response['error'] = 'El Especialista no Existe'
            status = 404
        except Exception as e:
            print(str(e))
            response['error'] = 'Error inesperado, Intente mas tarde'
            status = 500
        return JsonResponse(response, status=status)

