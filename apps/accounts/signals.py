from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (Admin, Especialista, Operador, AdminProfile,
                     EspecialistaProfile, OperadorProfile, CustomUser)


# @receiver(post_save, sender=CustomUser)
# def admin_post_save(sender, instance, created, **kwargs):
#     if created and instance.tipo == "ADM":
#         AdminProfile.objects.create(user=instance)


# @receiver(post_save, sender=CustomUser)
# def especialista_post_save(sender, instance, created, **kwargs):
#     if created and instance.tipo == "ESP":
#         EspecialistaProfile.objects.create(user=instance)


# @receiver(post_save, sender=CustomUser)
# def operador_post_save(sender, instance, created, **kwargs):
#     if created and instance.tipo == "OPE":
#         OperadorProfile.objects.create(user=instance)
