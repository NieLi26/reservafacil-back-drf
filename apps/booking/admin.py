from django.contrib import admin
from .models import (
    Tarifa, Especialidad, Categoria,
    Horario, Cliente, Cita, Pago,
    HistorialAnulacion
)
# Register your models here.


class EspecialidadInline(admin.TabularInline):
    model = Especialidad


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    inlines = [
        EspecialidadInline
    ]
    list_display = ('nombre', 'is_active')


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ('valor', 'is_active')


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'tarifa', 'is_active')
    raw_id_fields = ['tarifa', 'categoria']  # Crea una barra de busqueda en el campo


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('especialista', 'dia', 'inicio', 'termino', 'duracion')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'rut',
        'nombre',
        'primer_apellido',
        'segundo_apellido'
    )


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = (
        'cliente',
        'especialista',
        'especialidad',
        'fecha',
        'hora',
        'estado'
    )


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        'cita',
        'total',
        'folio',
        'cod_especialista',
        'metodo',
    )


@admin.register(HistorialAnulacion)
class HistorialAnulaciondmin(admin.ModelAdmin):
    list_display = (
        'cita',
        'motivo'
    )
# admin.site.register(Tarifa)
# admin.site.register(Especialidad)
# admin.site.register(Categoria)
