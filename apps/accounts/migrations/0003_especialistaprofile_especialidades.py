# Generated by Django 4.2.3 on 2023-07-12 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
        ('accounts', '0002_admin_especialista_operador_customuser_direccion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='especialistaprofile',
            name='especialidades',
            field=models.ManyToManyField(to='booking.especialidad'),
        ),
    ]