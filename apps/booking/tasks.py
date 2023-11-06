# from celery import shared_task
# from django.core.mail import BadHeaderError, EmailMultiAlternatives
# from django.http import HttpResponse
# from django.conf import settings
# from django.template.loader import get_template




# # @shared_task
# # def order_created(order_id):
# #     """
# #     Task to send an e-mail notification when an order is
# #     successfully created.
# #     """
# #     order = Order.objects.get(id=order_id)
# #     subject = f'Order nr. {order.id}'
# #     message = f'Dear {order.first_name},\n\n' \
# #               f'You have successfully placed an order.' \
# #               f'Your order ID is {order.id}.'
# #     mail_sent = send_mail(subject,
# #                           message,
# #                           'admin@myshop.com',
# #                           [order.email])
# #     return mail_sent

# # ========== Email con Adjunto y enviar Copia, MIME texto plano y html (EmailMultiAlternatives) ==========
# @shared_task
# def send_email_cita_task(to_email, cliente, profesional, especialidad, fecha, hora, template_html, subject, cc=None):
#     """ Ejemplo con para adjuntar contexto, html,css, archivo adjunto y multiples correos"""
#     try:
#         # genera instancia del template
#         template = get_template(template_html)
#         context = {
#             'cliente': cliente,
#             'profesional': profesional,
#             'especialidad': especialidad,
#             'fecha': fecha,
#             'hora': hora
#         }

#         # cargamos el contexto dentro del template
#         message = template.render(context)

#         if cc is None:
#             cc_list = []
#         else:
#             cc_list = cc

#         # Generamos instancia de EmailMultiAlternatives
#         email = EmailMultiAlternatives(
#             subject=subject,
#             body=message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[to_email],
#             bcc=cc_list
#         )
        
#         # convert the html and css inside the "contact_form.txt" in html template
#         email.content_subtype = 'html'

#         # opcional adjuntar(nombre archiv, contenido, tipo de contenido)
#         # email.attach(filename='', content='', mimetype='')

#         # Enviamos correo
#         email.send()

#         return HttpResponse('Mensaje enviado correctamente')
#     except BadHeaderError:
#         return HttpResponse('Se ha encontrado un asunto no valido')
#     except Exception as e:
#         print(str(e))
#         pass
