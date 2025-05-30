# Generated by Django 5.2 on 2025-04-29 13:42

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotspot_app', '0011_remove_hotspotusers_datesubscribed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotspotusers',
            name='dateSubscribed',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='hotspotusers',
            name='expectedExpiry',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='hotspotusers',
            name='plan',
            field=models.TextField(default=''),
        ),
    ]
