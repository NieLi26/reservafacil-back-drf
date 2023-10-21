from rest_framework import serializers
from datetime import datetime, timedelta, date
from .models import (
    Tarifa, Categoria, Cliente,
    Especialidad, Horario,
    Pago, Cita, HistorialAnulacion
)


class TarifaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tarifa
        fields = ('valor',)

    def validate_valor(self, value):
        # valor = self.context.get('valor')
        if Tarifa.objects.filter(valor__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            msg = 'Este valor ya esta en Uso'
            raise serializers.ValidationError(msg)
        if value <= 0:
            msg = 'Valor debe ser mayor a 0'
            raise serializers.ValidationError(msg)
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        # data['fecha'] = instance.created.strftime('%d/%m/%Y')
        data['fecha'] = instance.created.strftime('%Y/%m/%d')
        return data


class CategoriaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Categoria
        fields = ('nombre',)

    def validate_nombre(self, value):
        if Categoria.objects.filter(nombre__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            msg = 'Este nombre ya esta en Uso'
            raise serializers.ValidationError(msg)
        return value
 
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        data['fecha'] = instance.created.strftime('%Y/%m/%d')
        return data
    

class ClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cliente
        fields = ('nombre', 'primer_apellido', 'segundo_apellido', 'telefono',
                  'email', 'rut', 'fecha_nacimiento', 'sexo')

    def validate_rut(self, value):
        rut = value.lower()
        print(rut)
        if Cliente.objects.filter(rut__iexact=rut).exclude(pk=self.instance.pk if self.instance else None).exists():
            msg = 'Este rut ya se encuentra en uso'
            raise serializers.ValidationError(msg)
        return rut

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        return data
    

class EspecialidadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Especialidad
        fields = ('nombre', 'categoria', 'tarifa')

    def validate_nombre(self, value):
        if Especialidad.objects.filter(nombre__iexact=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            msg = 'Este nombre ya esta en Uso'
            raise serializers.ValidationError(msg)
        return value
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        data['categoria'] = CategoriaSerializer(instance.categoria).data
        data['tarifa'] = TarifaSerializer(instance.tarifa).data
        data['fecha'] = instance.created.strftime('%Y/%m/%d')
        return data
    

class HorarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Horario
        fields = ('especialista', 'dia', 'inicio', 'termino', 'duracion')

    def validate(self, attrs):
        # validated_data = super().clean()
        # inicio = validated_data.get('inicio')
        # termino = validated_data.get('termino')
        # duracion = validated_data.get('duracion')
        # especialista = validated_data.get('especialista')
        # dia = validated_data.get('dia')

        inicio = attrs.get('inicio')
        termino = attrs.get('termino')
        duracion = attrs.get('duracion')
        especialista = attrs.get('especialista')
        dia = attrs.get('dia')

        # ==== evitar hora de inicio mayor que la de termino, o igual
        if inicio and termino:
            if inicio > termino:
                msg = 'La hora de inicio no puede ser mayor a la hora de termino'
                # self.add_error('inicio', msg)
                raise serializers.ValidationError({'inicio': msg})
            if inicio == termino:
                msg = 'La hora  de inicio no puede ser igual a la hora de termino'
                # self.add_error('inicio', msg)
                raise serializers.ValidationError({'inicio': msg})

        # ==== Obliga a coincidir el rango horario con la duracion por consulta
        if duracion and termino and inicio:
            # obten un objeto timedelta en minutos
            duracion_timedelta = timedelta(minutes=duracion)
            # calcula la diferencia entre 2 datetime, generando un objeto timedelta
            tiempo_diferencia = datetime.combine(date.today(), termino) - datetime.combine(date.today(), inicio)
            # obtiene el sobrante de la division de los timedelta en segundos
            # condiciona si es distinto a 0 se devuelve un error
            if tiempo_diferencia.total_seconds() % duracion_timedelta.total_seconds() != 0:
                msg = 'La duración debe coincidir la hora de inicio y término'
                # self.add_error('duracion', msg)
                raise serializers.ValidationError({'duracion': msg})

        # ==== Evita la colision de horarios por dia y especialista
        # Obtener todos los horarios existentes para el especialista y día
        if especialista and dia and inicio and termino:
            superpuestos = Horario.objects.filter(
                especialista=especialista, dia=dia,
                inicio__lt=termino, termino__gt=inicio
            ).exclude(pk=self.instance.pk if self.instance else None)

            if superpuestos.exists():
                msg = 'El nuevo horario se superpone con un horario existente.'
                raise serializers.ValidationError({'Error': msg})
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        data['especialista'] = {
            'id': instance.especialista.id,
            'nombre': instance.especialista.user.username
        }
        data['inicio'] = instance.inicio.strftime("%H:%M")
        data['termino'] = instance.termino.strftime("%H:%M")
        return data


class PagoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pago
        fields = ('cita', 'total', 'cod_especialista', 'metodo', 'folio')

    def validate(self, attrs):
        # cleaned_data = super().clean()
        # metodo = cleaned_data.get('metodo')
        metodo = attrs.get('metodo')

        # Verificar si el valor del folio se envió en la petición
        if metodo == 'TA' or metodo == 'EF':
            # Establecer el valor por defecto si no se proporcionó en la petición
            attrs['folio'] = 'Sin Folio'
        return attrs
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        data['cliente'] = ClienteSerializer(instance.cita.cliente).data
        data['fecha'] = instance.created.strftime('%Y/%m/%d')
        return data


class CitaCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cita
        fields = ('especialista', 'especialidad', 'fecha', 'hora', 'motivo')

    # def clean_fecha(self):
    #     fecha = self.cleaned_data['fecha']
    #     especialista = self.cleaned_data['especialista']
    #     if fecha > especialista.termino_contrato:
    #         msg = 'Fecha de Cita no Disponible.'
    #         raise forms.ValidationError(msg)
    #     return fecha

    def validate(self, attrs):
        hora = attrs.get('hora')
        fecha = attrs.get('fecha')
        especialista = attrs.get('especialista')

        # Obtener la fecha actual
        fecha_actual = datetime.now().date()

        # restringir fechas menores a la actual
        if fecha < fecha_actual:
            msg = 'No puedes reservar en una fecha que ya paso'
            raise serializers.ValidationError({'fecha': msg})

        # Restringir reservar con 24 horas de anticipacion
        # Verificar si la fecha seleccionada es el día siguiente al actual
        if fecha == fecha_actual + timedelta(days=1):
            # Verificar si se cumplen las 24 horas de anticipación para reservar
            hora_actual = datetime.now().time()
            if not hora >= hora_actual:
                msg = 'Debes reservar con al menos 24 horas de anticipación.'
                raise serializers.ValidationError({'hora': msg})
     
        # Restringir fecha maxima de reserva por especialista
        if fecha > especialista.termino_contrato:
            msg = 'Fecha de Cita no Disponible.'
            raise serializers.ValidationError({'fecha': msg})
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        data['cliente'] = ClienteSerializer(instance.cliente).data
        data['especialista'] = {
            'id': instance.especialista.id,
            'nombre': instance.especialista.user.username
        }
        data['fecha'] = instance.fecha.strftime('%d/%m/%Y')
        data['hora'] = instance.hora.strftime("%H:%M")
        data['estado'] = instance.estado
        data['motivo_anulacion'] = instance.historiales_anulacion.first().motivo if instance.historiales_anulacion.first() else ''
        data['realizada'] = instance.realizada
        return data
    

class HistorialAnulacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = HistorialAnulacion
        fields = ('cita', 'motivo')

    def validate_cita(self, value):
        if value.estado == 'AN':
            msg = 'No se puede Anular una cita ya Anulada'
            raise serializers.ValidationError(msg)
        return value
    
