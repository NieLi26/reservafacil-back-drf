# Generated by Django 4.2.3 on 2023-07-16 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='horario',
            name='duracion',
            field=models.PositiveIntegerField(),
        ),
    ]