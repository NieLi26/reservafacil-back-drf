from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import send_email_cita
# from .tasks import send_email_cita_task
from .models import Cita, Pago, HistorialAnulacion


@receiver(post_save, sender=Cita)
def cita_post_save(sender, instance, created, **kwargs):
    if created:
        send_email_cita(instance.cliente.email,
                        f'{instance.cliente.nombre} {instance.cliente.primer_apellido}',
                        instance.especialista.user.get_full_name(),
                        instance.especialidad,
                        instance.fecha,
                        instance.hora,
                        'modules/cita/email_request.txt',
                        'Solicitud de reserva de cita')
    else:
        if instance.estado == 'AN':
            send_email_cita(instance.cliente.email,
                            f'{instance.cliente.nombre} {instance.cliente.primer_apellido}',
                            instance.especialista.user.get_full_name(),
                            instance.especialidad,
                            instance.fecha,
                            instance.hora,
                            'modules/cita/email_anulled.txt',
                            'Cita Anulada',
                            [instance.especialista.user.email])
       
        if instance.estado == 'CF':
            send_email_cita(instance.cliente.email,
                            f'{instance.cliente.nombre} {instance.cliente.primer_apellido}',
                            instance.especialista.user.get_full_name(),
                            instance.especialidad,
                            instance.fecha,
                            instance.hora,
                            'modules/cita/email_confirm.txt',
                            'Cita Confirmada',
                            [instance.especialista.user.email])


@receiver(post_save, sender=Pago)
def pago_post_save(sender, instance, created, **kwargs):
    if created:
        cita = Cita.objects.get(id=instance.cita.id)
        cita.estado = 'PA'
        cita.save()


@receiver(post_save, sender=HistorialAnulacion)
def historial_anulacion_post_save(sender, instance, created, **kwargs):
    if created:
        try:
            cita = Cita.objects.get(id=instance.cita.id)
            cita.estado = 'AN'
            cita.save()
        except Exception as e:
            print(str(e))
