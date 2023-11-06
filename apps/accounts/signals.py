from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import (Admin, Especialista, Operador, AdminProfile,
                     EspecialistaProfile, OperadorProfile, CustomUser)

User = get_user_model()

# @receiver(post_save, sender=User)
# def user_post_save(sender, instance, created, **kwargs):
#     if created:
#         Token.objects.create(user=instance)

    # if instance.tipo == "ESP":
    #     group = Group.objects.get(name='Especialista')
    #     instance.groups.add(group)
    # elif instance.tipo == "ADM":
    #     group = Group.objects.get(name='Administrador')
    #     instance.groups.add(group)


@receiver(post_save, sender=Especialista)
def especialista_post_save(sender, instance, created, **kwargs):
    if created and instance.tipo == "ESP":
        group = Group.objects.get(name='Especialista')
        instance.groups.add(group)


@receiver(post_save, sender=Especialista)
def especialista_post_delete(sender, instance, created, **kwargs):
    try:
        EspecialistaProfile.objects.get(user=instance).delete()
    except Exception as e:
        print(str(e))
        pass

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
