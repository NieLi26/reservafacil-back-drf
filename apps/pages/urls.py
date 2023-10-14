from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('agendar/', views.ReservaTemplateView.as_view(), name='reserva'),
    path('agendar/resumen/<int:id>/', views.ResumenTemplateView.as_view(),
         name='resumen'),
]
