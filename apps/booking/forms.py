from django import forms
from django.db.models import Q
from datetime import datetime, timedelta, date
from .models import (
    Cita, Cliente, Pago,
    HistorialAnulacion, Categoria, Especialidad,
    Tarifa, Horario
)
from apps.accounts.models import EspecialistaProfile


class CitaCreateForm(forms.ModelForm):

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

    def clean(self):
        # cleaned_data = self.cleaned_data
        cleaned_data = super().clean()
        hora = cleaned_data.get('hora')
        fecha = cleaned_data.get('fecha')
        especialista = cleaned_data.get('especialista')

        # Obtener la fecha actual
        fecha_actual = datetime.now().date()

        # restringir fechas menores a la actual
        if fecha < fecha_actual:
            msg = 'No puedes reservar en una fecha que ya paso'
            self.add_error('fecha', msg)

        # Restringir reservar con 24 horas de anticipacion
        # Verificar si la fecha seleccionada es el día siguiente al actual
        if fecha == fecha_actual + timedelta(days=1):
            # Verificar si se cumplen las 24 horas de anticipación para reservar
            hora_actual = datetime.now().time()
            if not hora >= hora_actual:
                msg = 'Debes reservar con al menos 24 horas de anticipación.'
                self.add_error('hora', msg)

        # Restringir fecha maxima de reserva por especialista
        if fecha > especialista.termino_contrato:
            msg = 'Fecha de Cita no Disponible.'
            self.add_error('fecha', msg)
        return cleaned_data


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = ('nombre', 'primer_apellido', 'segundo_apellido', 'telefono',
                  'email', 'rut', 'fecha_nacimiento', 'sexo')

    def clean_rut(self):
        rut = self.cleaned_data['rut']
        rut = rut.lower()
        if Cliente.objects.filter(rut=rut).exclude(pk=self.instance.pk).exists():
            msg = 'Este rut ya se encuentra en uso'
            raise forms.ValidationError(msg)
        return rut


class PagoForm(forms.ModelForm):

    class Meta:
        model = Pago
        fields = ('cita', 'total', 'cod_especialista', 'metodo', 'folio')

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo')

        # Verificar si el valor del folio se envió en la petición
        if metodo == 'TA' or metodo == 'EF':
            # Establecer el valor por defecto si no se proporcionó en la petición
            cleaned_data['folio'] = 'Sin Folio'
        return cleaned_data


class HistorialAnulacionForm(forms.ModelForm):

    class Meta:
        model = HistorialAnulacion
        fields = ('cita', 'motivo')

    def clean_cita(self):
        cita = self.cleaned_data['cita']
        if cita.estado == 'AN':
            msg = 'No se puede Anular una cita ya Anulada'
            raise forms.ValidationError(msg)
        return cita


class CategoriaForm(forms.ModelForm):
    
    class Meta:
        model = Categoria
        fields = ('nombre',)

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            msg = 'Este nombre ya esta en Uso'
            raise forms.ValidationError(msg)
        return nombre


class EspecialidadForm(forms.ModelForm):
    
    class Meta:
        model = Especialidad
        fields = ('nombre', 'categoria', 'tarifa')

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Especialidad.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            msg = 'Este nombre ya esta en Uso'
            raise forms.ValidationError(msg)
        return nombre


class TarifaForm(forms.ModelForm):

    class Meta:
        model = Tarifa
        fields = ('valor',)

    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if Tarifa.objects.filter(valor__iexact=valor).exclude(pk=self.instance.pk).exists():
            msg = 'Este valor ya esta en Uso'
            raise forms.ValidationError(msg)
        return valor


class HorarioForm(forms.ModelForm):

    class Meta:
        model = Horario
        fields = ('especialista', 'dia', 'inicio', 'termino', 'duracion')

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('inicio')
        termino = cleaned_data.get('termino')
        duracion = cleaned_data.get('duracion')
        especialista = cleaned_data.get('especialista')
        dia = cleaned_data.get('dia')

        # ==== evitar hora de inicio mayor que la de termino, o igual
        if inicio and termino:
            if inicio > termino:
                msg = 'La hora de inicio no puede ser mayor a la hora de termino'
                self.add_error('inicio', msg)
            if inicio == termino:
                msg = 'La hora  de inicio no puede ser igual a la hora de termino'
                self.add_error('inicio', msg)

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
                self.add_error('duracion', msg)

        # ==== Evita la colision de horarios por dia y especialista
        # Obtener todos los horarios existentes para el especialista y día
        if especialista and dia and inicio and termino:
            superpuestos = Horario.objects.filter(
                especialista=especialista, dia=dia,
                inicio__lt=termino, termino__gt=inicio
            ).exclude(pk=self.instance.pk)

            if superpuestos.exists():
                msg = 'El nuevo horario se superpone con un horario existente.'
                raise forms.ValidationError(msg)
        return cleaned_data


class CitaRealizadaForm(forms.Form):
    obs = forms.CharField(widget=forms.Textarea)
