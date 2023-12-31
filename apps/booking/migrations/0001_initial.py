# Generated by Django 4.2.3 on 2023-07-11 00:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_admin_especialista_operador_customuser_direccion_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('primero_apellido', models.CharField(max_length=150)),
                ('segundo_apellido', models.CharField(max_length=150)),
                ('nacionalidad', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=20)),
                ('email', models.CharField(max_length=50)),
                ('rut', models.CharField(max_length=10)),
                ('fecha_nacimiento', models.DateField()),
                ('sexo', models.CharField(choices=[('M', 'Masculino'), ('F', 'Femenino')], max_length=1)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
            },
        ),
        migrations.CreateModel(
            name='Tarifa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('valor', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Tarifa',
                'verbose_name_plural': 'Tarifas',
            },
        ),
        migrations.CreateModel(
            name='Valoracion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntuacion', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], max_length=1)),
                ('obs', models.TextField()),
                ('especialista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='valoraciones', to='accounts.especialistaprofile')),
            ],
            options={
                'verbose_name': 'Valoracion',
                'verbose_name_plural': 'Valoraciones',
            },
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.CharField(choices=[('LU', 'Lunes'), ('MA', 'Martes'), ('MI', 'Miercoles'), ('JU', 'Jueves'), ('Vi', 'Viernes'), ('SA', 'Sabado')], max_length=2)),
                ('inicio', models.TimeField()),
                ('termino', models.TimeField()),
                ('duracion', models.TimeField()),
                ('especialista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horarios', to='accounts.especialistaprofile')),
            ],
            options={
                'verbose_name': 'Horario',
                'verbose_name_plural': 'Horarios',
            },
        ),
        migrations.CreateModel(
            name='Especialidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=50)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Especialidades', to='booking.categoria')),
                ('tarifa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Especialidades', to='booking.tarifa')),
            ],
            options={
                'verbose_name': 'Especialidad',
                'verbose_name_plural': 'Especialidades',
            },
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('hora', models.TimeField()),
                ('motivo', models.TextField()),
                ('estado', models.CharField(choices=[('RE', 'Reservada'), ('TE', 'Terminada'), ('AN', 'Anulada'), ('PA', 'PAGADA')], max_length=2)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Citas', to='booking.cliente')),
                ('especialista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Citas', to='accounts.especialistaprofile')),
            ],
            options={
                'verbose_name': 'Cita',
                'verbose_name_plural': 'Citas',
            },
        ),
    ]
