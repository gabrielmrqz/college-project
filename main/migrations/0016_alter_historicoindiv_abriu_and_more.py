# Generated by Django 4.2 on 2023-05-09 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_rastreiolink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicoindiv',
            name='abriu',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='historicoindiv',
            name='enviados',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='historicoindiv',
            name='falhou',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='historicoindiv',
            name='passou',
            field=models.IntegerField(default=0),
        ),
    ]
