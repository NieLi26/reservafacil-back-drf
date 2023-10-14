from django.urls import path
# from rest_framework.routers import SimpleRouter

from . import views
from apps.booking.api.v1 import views as booking_views
from apps.booking.api.v2 import views as booking_views_v2


app_name = "v2"

urlpatterns = [
    # Tarifa
    # path(
    #     route='booking/tarifas',
    #     view=booking_views.TarifaListCreateAPIView.as_view(),
    #     name='booking-tarifa-list'
    # ),
    path(
        route='booking/tarifas/<str:id>/',
        view=booking_views.TarifaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-tarifa-detail'
    ),
    # Categoria
    path(
        route='booking/categorias',
        # view=booking_views.categoria_json,
        view=booking_views.CategoriaListCreateAPIView.as_view(),
        name='booking-categoria-list'
    ),
    path(
        route='booking/categorias/<str:id>',
        view=booking_views.CategoriaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-categoria-detail'
    ),
    # Especialidad
    path(
        route='booking/especialidades',
        # view=booking_views.especialidad_json,
        view=booking_views.EspecialidadListCreateAPIView.as_view(),
        name='booking-especialidad-list'
    ),
    path(
        route='booking/especialidades/<int:id>',
        view=booking_views.EspecialidadRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-especialidad-detail'
    ),
    # Especialista
    path(
        route='booking/especialistas',
        # view=booking_views.especialista_json,
        view=booking_views.EspecialistaListCreateAPIView.as_view(),
        name='booking-especialista-list'
    ),
    path(
        route='booking/especialistas/<int:id>',
        # view=booking_views.especialista_json,
        view=booking_views.EspecialistaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-especialista-detail'
    ),
    # Cita
    path(
        route='booking/citas',
        view=booking_views.CitaListCreateAPIView.as_view(),
        name='booking-cita-list'
    ),
    path(
        route='booking/citas/<int:id>',
        view=booking_views.CitaRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-cita-detail'
    ),
    # Horario
    path(
        route='booking/horarios',
        # view=booking_views.horario_json,
        view=booking_views.HorarioListCreateAPIView.as_view(),
        name='booking-horario-list'
    ),
    path(
        route='booking/horarios/<str:id>',
        view=booking_views.HorarioRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-horario-detail'
    ),
    # Cliente
    path(
        route='booking/clientes',
        view=booking_views.ClienteListCreateAPIView.as_view(),
        name='booking-cliente-list'
    ),
    path(
        route='booking/clientes/<str:rut>',
        view=booking_views.ClienteRetrieveUpdateDestroyAPIView.as_view(),
        name='booking-cliente-detail'
    ),
    # Pago
    path(
        route='booking/pagos',
        view=booking_views.PagoListCreateAPIView.as_view(),
        name='booking-pago-list'
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
    path('booking/tarifas', booking_views_v2.TarifaListCreateAPIView.as_view(), name='booking-tarifa-list'),
]