# Generated by Django 4.2.3 on 2023-07-16 04:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_alter_horario_duracion'),
    ]

    operations = [
        migrations.AddField(
            model_name='cita',
            name='especialidad',
            field=models.CharField(default=datetime.datetime(2023, 7, 16, 4, 1, 6, 548061, tzinfo=datetime.timezone.utc), max_length=250),
            preserve_default=False,
        ),
    ]
