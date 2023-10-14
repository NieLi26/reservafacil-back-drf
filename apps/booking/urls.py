from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.DashboardTemplateView.as_view(), name='dashboard'),
    path('cita/', views.CitaTemplateView.as_view(), name='cita'),
    path('categoria/', views.CategoriaTemplateView.as_view(), name='categoria'),
    path('especialidad/', views.EspecialidadTemplateView.as_view(), name='especialidad'),
    path('tarifa/', views.TarifaTemplateView.as_view(), name='tarifa'),
    path('pago/', views.PagoTemplateView.as_view(), name='pago'),
    path('horario/', views.HorarioTemplateView.as_view(), name='horario'),
    path('cliente/', views.ClienteTemplateView.as_view(), name='cliente'),
    path('especialista/', views.EspecialistaTemplateView.as_view(), name='especialista'),
]
