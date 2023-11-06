from django.urls import path
# from rest_framework.routers import SimpleRouter

from . import views
from apps.booking.api.v1 import views as booking_views
from apps.booking.api.v2 import views as booking_views_v2
from apps.accounts.api.v1 import views as accounts_views

app_name = "v2"

urlpatterns = [
    # path(
    #     route='booking/especialistas',
    #     # view=booking_views.especialista_json,
    #     view=booking_views.EspecialistaListCreateAPIView.as_view(),
    #     name='booking-especialista-list'
    # ),
    path(
        route='booking/especialistas/<int:id>',
        # view=booking_views.especialista_json,
        view=booking_views.EspecialistaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-especialista-detail'
    ),
]

urlpatterns += [
    path('get-csrf-token', views.get_csrf_token, name='get_csrf_token')
]

# router = SimpleRouter()

# router.register("lots", views.LotModelViewSet, basename="lots") 
# router.register("fares", views.FareModelViewSet, basename="fares") 
# router.register("fares-pagination", views.FareModelPaginationViewSet, basename="fares_pagination") 
# router.register("fares-period", views.FarePeriodModelViewSet, basename="fares_period") 
# router.register("fares-period-pagination", views.FarePeriodModelPaginationViewSet, basename="fares_period_pagination") 
# router.register("clients", views.ClientModelViewSet, basename="clients") 
# router.register("clients-pagination", views.ClientModelPaginationViewSet, basename="clients_pagination") 

# urlpatterns += router.urls

urlpatterns += [
    path(
        route='booking/tarifas',
        view=booking_views_v2.TarifaListCreateAPIView.as_view(),
        name='booking-tarifa-list'
    ),
    path(
        route='booking/tarifas/<int:id>',
        view=booking_views_v2.TarifaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-tarifa-detail'
    ),
    path(
        route='booking/categorias',
        view=booking_views_v2.CategoriaListCreateAPIView.as_view(),
        name='booking-categoria-list'
    ),
    path(
        route='booking/categorias/<int:id>',
        view=booking_views_v2.CategoriaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-categoria-detail'
    ),
    path(
        route='booking/clientes',
        view=booking_views_v2.ClienteListCreateAPIView.as_view(),
        name='booking-cliente-list'
    ),
    path(
        route='booking/clientes/<int:id>',
        view=booking_views_v2.ClienteRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-cliente-detail'
    ),
    path(
        route='booking/especialidades',
        view=booking_views_v2.EspecialidadListCreateAPIView.as_view(),
        name='booking-especialidad-list'
    ),
    path(
        route='booking/especialidades/<int:id>',
        view=booking_views_v2.EspecialidadRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-especialidad-detail'
    ),
    path(
        route='booking/horarios',
        view=booking_views_v2.HorarioListCreateAPIView.as_view(),
        name='booking-horario-list'
    ),
    path(
        route='booking/horarios/<int:id>',
        view=booking_views_v2.HorarioRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-horario-detail'
    ),
    path(
        route='booking/pagos',
        view=booking_views_v2.PagoListCreateAPIView.as_view(),
        name='booking-pago-list'
    ),
    path(
        route='booking/pagos/<int:id>',
        view=booking_views_v2.PagoRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-pago-detail'
    ),
    path(
        route='booking/citas',
        view=booking_views_v2.CitaListCreateAPIView.as_view(),
        name='booking-cita-list'
    ),
    path(
        route='booking/citas/<int:id>',
        view=booking_views_v2.CitaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-cita-detail'
    ),
    path(
        route='booking/historial-anulaciones',
        view=booking_views_v2.HistorialAnulacionListCreateAPIView.as_view(),
        name='booking-historial-anulacion-list'
    ),
    path(
        route='booking/especialistas',
        view=accounts_views.EspecialistaListCreateAPIView.as_view(),
        name='booking-especialista-list'
    ),
]

urlpatterns += [
    path(
        route='booking/categorias-listado/',
        view=booking_views_v2.categorias_json,
        name='booking-categoria-listado'
    ),
    path(
        route='booking/especialidades-listado/',
        view=booking_views_v2.especialidades_json,
        name='booking-especialidad-listado'
    ),
    path(
        route='booking/tarifas-listado/',
        view=booking_views_v2.tarifas_json,
        name='booking-tarifa-listado'
    ),
    path(
        route='booking/especialistasprofile-listado/',
        view=booking_views_v2.especialistas_profile_json,
        name='booking-especialista-listado'
    ),
    path(
        route='booking/citas-listado/',
        view=booking_views_v2.citas_json,
        name='booking-cita-listado'
    ),
    path(
        route='booking/horarios-especialista-listado/',
        view=booking_views_v2.horarios_especialista_json,
        name='booking-horario-especialista-listado'
    ),
    path(
        route='booking/cliente-rut/<str:rut>',
        view=booking_views_v2.cliente_rut_json,
        name='booking-cliente-rut'
    ),
    path(
        route='booking/cita-estado/<int:id>',
        view=booking_views_v2.CambiarEstadoCitaAPIView.as_view(),
        name='booking-cita-estado'
    ),
    path(
        route='booking/crear-cita/',
        view=booking_views_v2.AgendarCitaAPIView.as_view(),
        name='booking-crear-cita'
    ),
    path(
        route='booking/resumen-cita/<int:numero_cita>',
        view=booking_views_v2.ResumenCitaAPIView.as_view(),
        name='booking-resumen-cita'
    ),
    
]