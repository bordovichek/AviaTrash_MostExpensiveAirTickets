# Generated by Django 5.1.4 on 2024-12-22 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aviaticket', '0007_alter_flight_flight_to'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='flight_photo',
        ),
    ]
