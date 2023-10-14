from typing import Any
from django.core.management.base import BaseCommand
from apps.booking.models import Categoria, Especialidad, Tarifa


class Command(BaseCommand):
    help = 'Cargar Datos'

    def handle(self, *args: Any, **options: Any) -> str | None:
        # Categoria
        Tarifa.objects.all().delete()
        if not Tarifa.objects.count():
            tarifas = [20000, 40000, 60000]
            for tarifa in tarifas:
                Tarifa.objects.create(valor=tarifa)
        Categoria.objects.all().delete()
        if not Categoria.objects.count():
            categorias = ['Adolescencia', 'Cardiología Adulto',
                          'Cirugía Adulto']
            sub_categorias = {
                'Adolescencia': ['[todos]', 'Endocrinologia Adolescente',
                                 'Pediatria Adolescente',
                                 'Psicologia Adolescente'],
                'Cardiología Adulto': ['[Todos]', 'Arritmias',
                                       'Electrofisiología',
                                       'Marcapasos'],
                'Cirugía Adulto': ['Cirugía Bariátrica Y Metabólica',
                                   'Cirugía De Cabeza, Cuello Y Tiroides',
                                   'Cirugía De Hernias']                
            }
            current_tarifa = Tarifa.objects.first()
            print(current_tarifa)
            for categoria in categorias:
                nueva_categoria = Categoria.objects.create(nombre=categoria)
                if categoria in sub_categorias:
                    subcategorias = sub_categorias[categoria]
                    for subcategoria in subcategorias:
                        Especialidad.objects.create(categoria=nueva_categoria,
                                                    tarifa=current_tarifa,
                                                    nombre=subcategoria)
