# Generated by Django 4.2.3 on 2023-07-17 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0004_alter_horario_dia_excepcionhorario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cita',
            name='estado',
            field=models.CharField(choices=[('RE', 'Reservada'), ('TE', 'Terminada'), ('AN', 'Anulada'), ('PA', 'PAGADA')], default='RE', max_length=2),
        ),
    ]
