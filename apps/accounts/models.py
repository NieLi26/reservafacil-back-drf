from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUser(AbstractUser):
    class Tipos(models.TextChoices):
        ADMIN = "ADM", "Admin"
        ESPECIALISTA = "ESP", "Especialista"
        OPERADOR = "OPE", "Operador"

    base_type = Tipos.ADMIN

    class Sexos(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'
        NO_BINARIO = 'NB', 'No Binario'
        NO_DECIR = 'NO', 'Prefiero no Decirlo'

    # Que tipo de usuario somos?
    tipo = models.CharField(max_length=3, choices=Tipos.choices,
                            default=Tipos.ADMIN)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=250)
    nacionalidad = models.CharField(max_length=100)
    rut = models.CharField(max_length=10)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    sexo = models.CharField(max_length=2, choices=Sexos.choices)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.tipo = self.base_type

        return super().save(*args, **kwargs)

    def get_data(self):
        return {
            'id': self.id,
            'password': self.password,
            'username': self.username,
            'nombre': self.get_full_name(),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'telefono': self.telefono if self.telefono else '',
            'direccion': self.direccion,
            'nacionalidad': self.nacionalidad if self.nacionalidad else '',
            'email': self.email if self.email else '',
            'rut': self.rut if self.rut else '',
            'fecha_nacimiento': self.fecha_nacimiento.strftime('%d/%m/%Y') if self.fecha_nacimiento else '',
            'sexo': self.sexo if self.sexo else '',
            'fecha_creacion': self.date_joined.strftime('%d/%m/%Y')
        }


# Managers
class AdminManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs) \
                      .filter(tipo=CustomUser.Tipos.ADMIN)


class EspecialistaManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs) \
                      .filter(tipo=CustomUser.Tipos.ESPECIALISTA)


class OperadorManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs) \
                      .filter(tipo=CustomUser.Tipos.OPERADOR)


# Proxy Models
class Admin(CustomUser):
    base_type = CustomUser.Tipos.ADMIN
    objects = AdminManager()

    class Meta:
        proxy = True


class Especialista(CustomUser):
    base_type = CustomUser.Tipos.ESPECIALISTA
    objects = EspecialistaManager()

    class Meta:
        proxy = True

    # @property
    # def extra(self):
    #     return self.inventorprofile


class Operador(CustomUser):
    base_type = CustomUser.Tipos.OPERADOR
    objects = OperadorManager()

    class Meta:
        proxy = True


# Profiles
class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username


class EspecialistaProfile(models.Model):
    especialidades = models.ManyToManyField("booking.Especialidad")
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    info = models.TextField()
    inicio_contrato = models.DateField()
    termino_contrato = models.DateField()

    def __str__(self) -> str:
        return self.user.username

    def get_data(self):
        return {
            'id': self.id,
            # 'especialidades': [especialidad.nombre for especialidad in self.especialidades.all()],
            'especialidades': list(self.especialidades.values()),
            'nombre': self.user.username,
            'horarios': [horario.get_data() for horario in self.horarios.all()],
            # 'horarios': list(self.horarios.values()),
            'info': self.info,
            'inicio_contrato': self.inicio_contrato,
            'termino_contrato': self.termino_contrato,
            'user': self.user.get_data()
        }


class OperadorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username