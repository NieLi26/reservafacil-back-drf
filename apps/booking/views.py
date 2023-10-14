from typing import Any
from django import http
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, TemplateView
from .mixins import CustomPermissionRequiredMixin
from .models import Cita


class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'views/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        citas = Cita.objects.all()
        context['totales'] = citas.count()
        context['reservadas'] = citas.filter(estado='RS').count()
        context['confirmadas'] = citas.filter(estado='CF').count()
        context['anuladas'] = citas.filter(estado='AN').count()
        context['pagadas'] = citas.filter(estado='PA').count()
        return context


class CitaTemplateView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):
    permission_required = ('booking.view_cita',)
    template_name = 'views/cita.html'


class CategoriaTemplateView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):
    permission_required = ('booking.view_categoria',)
    template_name = 'views/categoria.html'


class EspecialidadTemplateView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):
    permission_required = ('booking.view_especialidad',)
    template_name = 'views/especialidad.html'


class TarifaTemplateView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):
    permission_required = ('booking.view_tarifa',)
    template_name = 'views/tarifa.html'


class PagoTemplateView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):
    permission_required = ('booking.view_pago',)
    template_name = 'views/pago.html'


class HorarioTemplateView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):
    permission_required = ('booking.view_horario',)
    template_name = 'views/horario.html'


class ClienteTemplateView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):
    permission_required = ('booking.view_cliente',)
    template_name = 'views/cliente.html'


class EspecialistaTemplateView(LoginRequiredMixin, CustomPermissionRequiredMixin, TemplateView):
    permission_required = ('booking.view_especialista',)
    template_name = 'views/especialista.html'
