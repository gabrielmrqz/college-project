# Generated by Django 4.2 on 2023-04-27 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_templates_alter_agendados_data_hora'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricoIndiv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
                ('email', models.TextField()),
                ('setor', models.CharField(max_length=40)),
                ('enviados', models.IntegerField()),
                ('falhou', models.IntegerField()),
                ('passou', models.IntegerField()),
            ],
        ),
    ]