# Generated by Django 5.1.7 on 2025-05-17 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0006_alter_flightschedule_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flightschedule',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=8, null=True),
        ),
    ]
