# Generated by Django 4.2.3 on 2023-07-27 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0009_alter_cita_especialista_alter_cliente_sexo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cita',
            name='estado',
            field=models.CharField(choices=[('RS', 'Reservada'), ('RL', 'Realizada'), ('AN', 'Anulada'), ('PA', 'Pagada')], default='RS', max_length=2),
        ),
    ]