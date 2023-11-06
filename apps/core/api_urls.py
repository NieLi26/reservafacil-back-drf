from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.booking.api.v1 import views as booking_views
from apps.accounts.api.v1 import views as accounts_views

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
        route='booking/horario/json/<int:id>/',
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

urlpatterns += [
    path(
        route='accounts/especialistas-especialidad-listado/',
        view=accounts_views.especialistas_especialidad_json,
        name='booking-especialista-especialidad-listado'
    ),
    path(
        route='accounts/especialistas/',
        view=accounts_views.EspecialistaListCreateAPIView.as_view(),
        name="accounts-especialista-list"
    ),
    path(
        route='accounts/especialistas/<int:id>/',
        view=accounts_views.EspecialistaRetrieveUpdateDestroyAPIView.as_view(),
        name="accounts-especialista-detail"
    ),

    # opcion 1 
    # path(
    #     route='accounts/login1',
    #     view=accounts_views.login,
    #     name='login'
    # ),
    # path(
    #     route='accounts/signup',
    #     view=accounts_views.signup
    # ),
    # path(
    #     route='accounts/test-token',
    #     view=accounts_views.test_token
    # ), 
    # opcion 2 
    # path(
    #     route='accounts/register',
    #     view=accounts_views.UserRegister.as_view()
    # ),
    # path(
    #     route='accounts/login2',
    #     view=accounts_views.UserLogin.as_view()
    # ),
    # path(
    #     route='accounts/logout',
    #     view=accounts_views.UserLogout.as_view()
    # ),
    # path(
    #     route='accounts/user',
    #     view=accounts_views.UserView.as_view()
    # ),

    ###### authtoken view DJANGO REST from django world videos ######
    path(
        route='accounts/login/',
        view=obtain_auth_token,
        name="login"
    ),
    path(
        route='accounts/logout/',
        view=accounts_views.logout,
        name="logout"
    ),
    path(
        route='accounts/register/',
        view=accounts_views.user_register,
        name="register"
    ),
    ###### authtoken viewJWT ######
    path(
        route='accounts/usuarios/perfil/',
        view=accounts_views.UserProfile.as_view(),
        name="accounts-usuario-perfil"
    ),
    path('accounts/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # para logearse y obtener token access y token refresh
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # para generara un nuevo token access en base al toke nrefresh
]