# Generated by Django 5.1.6 on 2025-03-27 09:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panels', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 3, 9, 11, 26, 500196, tzinfo=datetime.timezone.utc)),
        ),
    ]
