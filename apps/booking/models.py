from django.db import models
from django.db.models import Q
from datetime import timedelta, datetime, time
from apps.core.models import TimeStampedModel
from apps.accounts.models import EspecialistaProfile


class Categoria(TimeStampedModel):
    '''Model definition for Categoria.'''
    nombre = models.CharField(max_length=50)

    class Meta:
        '''Meta definition for Categoria.'''

        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nombre

    def get_data(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'fecha': self.created.strftime('%d/%m/%Y')
        }


class Tarifa(TimeStampedModel):
    '''Model definition for Tarifa.'''
    valor = models.PositiveIntegerField()

    class Meta:
        '''Meta definition for Tarifa.'''

        verbose_name = 'Tarifa'
        verbose_name_plural = 'Tarifas'

    def __str__(self):
        return str(self.valor)
    
    def get_data(self):
        return {
            'id': self.id,
            'valor': self.valor,
            'fecha': self.created.strftime('%d/%m/%Y')
        }


class Especialidad(TimeStampedModel):
    '''Model definition for Especialidad.'''
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE,
                                  related_name='Especialidades')
    tarifa = models.ForeignKey(Tarifa, on_delete=models.CASCADE,
                               related_name='Especialidades')
    nombre = models.CharField(max_length=50)

    class Meta:
        '''Meta definition for Categoria.'''

        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'

    def __str__(self):
        return self.nombre

    def get_data(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tarifa': self.tarifa.get_data(),
            'categoria': self.categoria.get_data(),
            'fecha': self.created.strftime('%d/%m/%Y')
        }


class Horario(TimeStampedModel):
    class Dias(models.TextChoices):
        LUNES = 'LU', 'Lunes'
        MARTES = 'MA', 'Martes'
        MIERCOLES = 'MI', 'Miercoles'
        JUEVES = 'JU', 'Jueves'
        VIERNES = 'Vi', 'Viernes'
        SABADO = 'SA', 'Sabado'
        DOMINGO = 'DO', 'Domingo'

    '''Model definition for Horario.'''
    especialista = models.ForeignKey(EspecialistaProfile,
                                     on_delete=models.CASCADE,
                                     related_name='horarios')
    dia = models.CharField(max_length=2, choices=Dias.choices)
    inicio = models.TimeField()
    termino = models.TimeField()
    duracion = models.PositiveIntegerField()

    class Meta:
        '''Meta definition for Horario.'''

        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'

    def __str__(self):
        return f'{self.inicio} - {self.termino}'

    # def get_horas_disponibles(self, fecha=None):
    #     horas_disponibles = []
    #     hora_actual = datetime.combine(datetime.min, self.inicio)
    #     duracion = timedelta(minutes=self.duracion)
    #     limite_termino = time(self.termino.hour, self.termino.minute)

    #     # era posible solucion pero me devuelve los horarios vacios
    #     # pero lso otros datos del especialista de lso devuelve y yo no los uso
    #     # necesito un objeto vacio nada mas, y eso lo hago en la view
    #     # Verificar si la fecha solicitada está dentro del rango del contrato
    #     # if fecha and fecha > self.especialista.termino_contrato:
    #     #     return horas_disponibles

    #     while hora_actual.time() < limite_termino:
    #         hora_actual_str = hora_actual.strftime("%H:%M")
    #         if fecha:
    #             citas_tomadas = self.especialista.citas.filter(fecha=fecha,
    #                                                            estado='RS')\
    #                 .values_list('hora', flat=True)
    #             citas_tomadas_str = [hora.strftime("%H:%M") for hora in citas_tomadas]
    #             if hora_actual_str not in citas_tomadas_str:
    #                 horas_disponibles.append(hora_actual_str)
    #             hora_actual += duracion
    #         else:
    #             horas_disponibles.append(hora_actual_str)
    #             hora_actual += duracion
    #     return horas_disponibles

    def get_horas_disponibles(self, fecha=None):
        if fecha is None:
            fecha = datetime.now().date()
        horas_disponibles = []
        limite_inicio = datetime.combine(fecha, self.inicio)
        duracion = timedelta(minutes=self.duracion) # tiempo para manipular con fechas
        limite_termino = self.termino

        while limite_inicio.time() < limite_termino:
            hora_actual_str = limite_inicio.time().strftime("%H:%M")  # convertir datetime hora_actual en formato str de hora y minuto
            if fecha:
                # Buscar todas las citas tomadas con esa fecha y estado y devolver listado de objeto time de cada una
                citas_tomadas = self.especialista.citas \
                    .filter(
                        Q(fecha=fecha, estado='RS') |
                        Q(fecha=fecha, estado='RL') |
                        Q(fecha=fecha, estado='CF')
                    ).values_list('hora', flat=True)
                # Convertir objeto time en format str de hora y minuto, y devolver un array.
                citas_tomadas_str = [hora.strftime("%H:%M") for hora in citas_tomadas]
                # Comprobar si dentro del array, existe la hora actual que se quiere tomar
                if hora_actual_str not in citas_tomadas_str:
                    # Verificar que la hora actual sea posterior al límite de tiempo
                    if limite_inicio.date() == (datetime.now() + timedelta(days=1)).date():
                        if limite_inicio.time() >= datetime.now().time():
                            horas_disponibles.append(hora_actual_str)
                    else:
                        horas_disponibles.append(hora_actual_str)
            else:
                # Verificar que la hora actual sea posterior al límite de tiempo
                if limite_inicio.time() >= datetime.now().time():
                    horas_disponibles.append(hora_actual_str)

            # Sumar la duración a la hora actual
            limite_inicio += duracion

        return horas_disponibles

    def get_data(self, fecha=None):
        return {
            'id': self.id,
            'especialista': {
                'id': self.especialista.id,
                'nombre': self.especialista.user.username,
            },
            'fecha_limite': self.especialista.termino_contrato,
            'dia': self.dia,
            # 'inicio': self.inicio,
            # 'termino': self.termino,
            'inicio': self.inicio.strftime("%H:%M"),
            'termino': self.termino.strftime("%H:%M"),
            'duracion': self.duracion,
            'horas_disponibles': self.get_horas_disponibles(fecha)
        }


class ExcepcionHorario(TimeStampedModel):
    especialista = models.ForeignKey(EspecialistaProfile,
                                     on_delete=models.CASCADE,
                                     related_name='excepciones_horario')
    fecha = models.DateField()


class Valoracion(TimeStampedModel):
    class Puntuaciones(models.TextChoices):
        UNO = '1', '1'
        DOS = '2', '2'
        TRES = '3', '3'
        CUATRO = '4', '4'
        CINCO = '5', '5'

    '''Model definition for Valoracion.'''
    especialista = models.ForeignKey(EspecialistaProfile,
                                     on_delete=models.CASCADE,
                                     related_name='valoraciones')
    puntuacion = models.CharField(max_length=1, choices=Puntuaciones.choices)
    obs = models.TextField()

    class Meta:
        '''Meta definition for Valoracion.'''

        verbose_name = 'Valoracion'
        verbose_name_plural = 'Valoraciones'

    def __str__(self):
        pass


class Cliente(TimeStampedModel):
    class Sexos(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'
        NO_BINARIO = 'NB', 'No Binario'
        NO_DECIR = 'NO', 'Prefiero no Decirlo'

    '''Model definition for Cliente.'''
    nombre = models.CharField(max_length=150)
    primer_apellido = models.CharField(max_length=150)
    segundo_apellido = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    rut = models.CharField(max_length=10)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=2, choices=Sexos.choices)

    class Meta:
        '''Meta definition for Cliente.'''

        permissions = [('can_add_new_cliente', 'can add new cliente')]
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.rut

    def get_full_name(self):
        return f'{self.nombre} {self.primer_apellido} {self.segundo_apellido}'

    def get_data(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'primer_apellido': self.primer_apellido,
            'segundo_apellido': self.segundo_apellido,
            'telefono': self.telefono,
            'email': self.email,
            'rut': self.rut,
            'fecha_nacimiento': self.fecha_nacimiento.strftime('%d/%m/%Y'),
            'sexo': self.sexo,
        }


class Cita(TimeStampedModel):
    class Estados(models.TextChoices):
        RESERVADA = 'RS', 'Reservada'
        CONFIRMADA = 'CF', 'Confirmada'
        # REALIZADA = 'RL', 'Realizada'
        ANULADA = 'AN', 'Anulada'
        PAGADA = 'PA', 'Pagada'

    '''Model definition for Cita.'''
    cliente = models.ForeignKey(Cliente,
                                on_delete=models.CASCADE,
                                related_name='Citas')
    especialista = models.ForeignKey(EspecialistaProfile,
                                     on_delete=models.CASCADE,
                                     related_name='citas')
    especialidad = models.CharField(max_length=250)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=2, choices=Estados.choices,
                              default=Estados.RESERVADA)
    obs = models.TextField(blank=True)
    realizada = models.BooleanField(default=False)

    class Meta:
        '''Meta definition for Cita.'''

        ordering = ('cliente__nombre', )
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'

    def __str__(self):
        return self.cliente.rut

    def get_data(self):
        return {
            'id': self.id,
            'cliente': {
                'rut': self.cliente.rut,
                'nombre': self.cliente.get_full_name()
            },
            'especialista': self.especialista.user.username,
            'especialidad': self.especialidad,
            'fecha': self.fecha.strftime('%d/%m/%Y'),
            'hora': self.hora.strftime("%H:%M"),
            'estado': self.estado,
            'motivo': self.motivo,
            'motivo_anulacion': self.historiales_anulacion.first().motivo if self.historiales_anulacion.first() else '',
            'realizada': self.realizada
        }


class HistorialAnulacion(TimeStampedModel):
    '''Model definition for HistorialAnulacion.'''
    cita = models.ForeignKey(Cita,
                             on_delete=models.CASCADE,
                             related_name="historiales_anulacion")
    motivo = models.TextField()

    class Meta:
        '''Meta definition for HistorialAnulacion.'''

        verbose_name = 'HistorialAnulacion'
        verbose_name_plural = 'HistorialAnulaciones'

    def __str__(self):
        return f'{self.cita.id} / {self.cita.cliente.rut}'


class Pago(TimeStampedModel):
    class Metodos(models.TextChoices):
        TARJETA = 'TA', 'Tarjeta'
        EFECTIVO = 'EF', 'Efectivo'
        FONASA = 'FO', 'Fonasa'
        ISAPRE = 'IS', 'Isapre'
        CONVENIO = 'CO', 'Convenio'

    '''Model definition for Pago.'''
    cita = models.ForeignKey(Cita,
                             on_delete=models.CASCADE,
                             related_name='Pagos')
    total = models.PositiveIntegerField(default=0)
    folio = models.CharField(max_length=20, blank=True)
    cod_especialista = models.CharField(max_length=20)
    metodo = models.CharField(max_length=2, choices=Metodos.choices)

    class Meta:
        '''Meta definition for Pago.'''

        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return self.folio
    
    def get_data(self):
        return {
            'id': self.id,
            'cliente': {
                'rut': self.cita.cliente.rut,
                'nombre': self.cita.cliente.get_full_name()
            },
            'total': self.total,
            'cita': self.cita.id,
            'folio': self.folio,
            'cod_especialista': self.cod_especialista,
            'metodo': self.metodo,
            'fecha': self.created.strftime('%d/%m/%Y')
        }