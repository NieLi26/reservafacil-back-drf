# Generated by Django 4.2.3 on 2023-10-15 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0016_alter_cliente_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarifa',
            name='valor',
            field=models.PositiveIntegerField(),
        ),
    ]
