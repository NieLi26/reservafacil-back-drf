# Generated by Django 4.2.3 on 2023-07-17 04:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_especialistaprofile_especialidades'),
        ('booking', '0003_cita_especialidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='horario',
            name='dia',
            field=models.CharField(choices=[('LU', 'Lunes'), ('MA', 'Martes'), ('MI', 'Miercoles'), ('JU', 'Jueves'), ('Vi', 'Viernes'), ('SA', 'Sabado'), ('DO', 'Domingo')], max_length=2),
        ),
        migrations.CreateModel(
            name='ExcepcionHorario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('fecha', models.DateField()),
                ('especialista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='excepciones_horario', to='accounts.especialistaprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]