# Generated by Django 5.2 on 2025-04-28 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotspot_app', '0004_rename_date_subscribed_paymenthistory_datesubscribed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenthistory',
            name='MpesaReceiptNumber',
            field=models.TextField(default=''),
        ),
    ]
