# Generated by Django 5.1.3 on 2025-03-18 10:39

import django.contrib.gis.db.models.fields
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeoLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', django.contrib.gis.db.models.fields.PointField(geography=True, help_text='Geographic location (latitude and longitude)', srid=4326)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, help_text='When this location was recorded')),
            ],
        ),
    ]
