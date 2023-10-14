from django.urls import path
from apps.booking.api.v1 import views as booking_views

app_name = "v1"

urlpatterns = [
    # Tarifa
    path(
        route='booking/tarifa/json/',
        view=booking_views.TarifaListCreateAPIView.as_view(),
        name='booking-tarifa-list'
    ),
    path(
        route='booking/tarifa/json/<str:id>/',
        view=booking_views.TarifaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-tarifa-detail'
    ),
    # Categoria
    path(
        route='booking/categoria/json/',
        # view=booking_views.categoria_json,
        view=booking_views.CategoriaListCreateAPIView.as_view(),
        name='booking-categoria-list'
    ),
    path(
        route='booking/categoria/json/<str:id>/',
        view=booking_views.CategoriaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-categoria-detail'
    ),
    # Especialidad
    path(
        route='booking/especialidad/json/',
        # view=booking_views.especialidad_json,
        view=booking_views.EspecialidadListCreateAPIView.as_view(),
        name='booking-especialidad-list'
    ),
    path(
        route='booking/especialidad/json/<int:id>/',
        view=booking_views.EspecialidadRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-especialidad-detail'
    ),
    # Especialista
    path(
        route='booking/especialista/json/',
        # view=booking_views.especialista_json,
        view=booking_views.EspecialistaListCreateAPIView.as_view(),
        name='booking-especialista-list'
    ),

    path(
        route='booking/especialista/json/<int:id>/',
        # view=booking_views.especialista_json,
        view=booking_views.EspecialistaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-especialista-detail'
    ),
    # Cita
    path(
        route='booking/cita/json/',
        view=booking_views.CitaListCreateAPIView.as_view(),
        name='booking-cita-list'
    ),

    path(
        route='booking/cita/json/<int:id>/',
        view=booking_views.CitaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-cita-detail'
    ),
    # Horario
    path(
        route='booking/horario/json/',
        # view=booking_views.horario_json,
        view=booking_views.HorarioListCreateAPIView.as_view(),
        name='booking-horario-list'
    ),
    path(
        route='booking/horario/json/<str:id>/',
        view=booking_views.HorarioRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-horario-detail'
    ),
    # Cliente
    path(
        route='booking/cliente/json/',
        view=booking_views.ClienteListCreateAPIView.as_view(),
        name='booking-cliente-list'
    ),
    path(
        route='booking/cliente/json/<str:rut>/',
        view=booking_views.ClienteRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-cliente-detail'
    ),
    # Pago
    path(
        route='booking/pago/json/',
        view=booking_views.PagoListCreateAPIView.as_view(),
        name='booking-pago-list'
    ),
]