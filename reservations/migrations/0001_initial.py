# Generated by Django 5.1.7 on 2025-05-16 17:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlightSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_number', models.CharField(max_length=10)),
                ('origin', models.CharField(max_length=100)),
                ('destination', models.CharField(max_length=100)),
                ('departure_date', models.DateField()),
                ('departure_time', models.TimeField()),
                ('available_seats', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='FlightReservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('seats_booked', models.PositiveIntegerField()),
                ('flight_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='reservations.flightschedule')),
            ],
        ),
    ]
