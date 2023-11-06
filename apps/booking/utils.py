import datetime
import random
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.http import HttpResponse
from django.db.models import Q
# from django.shortcuts import redirect
from django.conf import settings
from django.template.loader import get_template

from .models import Cita


# ========== Email con Adjunto y enviar Copia, MIME texto plano y html (EmailMultiAlternatives) ==========
def send_email_cita(to_email, cliente, profesional, especialidad, fecha, hora, template_html, subject, cc=None):
    """ Ejemplo con para adjuntar contexto, html,css, archivo adjunto y multiples correos"""
    try:
        # genera instancia del template
        template = get_template(template_html)
        context = {
            'cliente': cliente,
            'profesional': profesional,
            'especialidad': especialidad,
            'fecha': fecha,
            'hora': hora
        }

        # cargamos el contexto dentro del template
        message = template.render(context)

        if cc is None:
            cc_list = []
        else:
            cc_list = cc

        # Generamos instancia de EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            bcc=cc_list
        )
        
        # convert the html and css inside the "contact_form.txt" in html template
        email.content_subtype = 'html'

        # opcional adjuntar(nombre archiv, contenido, tipo de contenido)
        # email.attach(filename='', content='', mimetype='')

        # Enviamos correo
        email.send()

        return HttpResponse('Mensaje enviado correctamente')
    except BadHeaderError:
        return HttpResponse('Se ha encontrado un asunto no valido')
    except Exception as e:
        print(str(e))
        pass


def validar_citas_cliente_fecha(cliente, fecha):
    total_citas = Cita.objects.filter(
        Q(fecha=fecha, estado='RS', cliente=cliente) |
        Q(fecha=fecha, estado='RL', cliente=cliente) |
        Q(fecha=fecha, estado='CF', cliente=cliente)
    ).count()
    return total_citas >= 3


def validar_cita_confirmada(id):
    try:
        cita = Cita.objects.get(id=id)
        if cita.estado == 'CF':
            return True
    except Cita.DoesNotExist:
        pass
    except Exception as e:
        print(str(e))
    return False


# def generar_numero_random(cantidad_digitos):
#     fecha_hora_actual = datetime.datetime.now()
#     numero = fecha_hora_actual.strftime('%Y%m%d%H%M%S')

#     # Verifica si se necesitan dígitos adicionales
#     digitos_faltantes = cantidad_digitos - len(numero)
#     if digitos_faltantes > 0:
#         numero += ''.join(random.choice('0123456789') for _ in range(digitos_faltantes))

#     return numero