from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
# from .tasks import sleeptime

from apps.booking.models import Cita


def home(request):
    # sleeptime.delay(15)
    return render(request, 'views/home.html')


def contact(request):
    return render(request, 'views/contact.html')


class ReservaTemplateView(TemplateView):
    template_name = 'views/reserva.html'


class ResumenTemplateView(TemplateView):
    template_name = 'views/resumen.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cita'] = get_object_or_404(Cita, pk=kwargs['id'])
        return context
