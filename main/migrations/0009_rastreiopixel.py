# Generated by Django 4.2 on 2023-04-29 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_historico_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='RastreioPixel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_pixel', models.IntegerField()),
                ('nome_campanha', models.TextField()),
                ('email', models.TextField()),
            ],
        ),
    ]
