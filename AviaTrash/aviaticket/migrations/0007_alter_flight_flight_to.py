# Generated by Django 5.1.4 on 2024-12-22 14:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aviaticket', '0006_citywithphoto_flight_flight_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='flight_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='aviaticket.citywithphoto', verbose_name='Куда'),
        ),
    ]
