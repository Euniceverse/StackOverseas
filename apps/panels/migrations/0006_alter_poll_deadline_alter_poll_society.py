# Generated by Django 5.1.6 on 2025-03-26 17:54

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panels', '0005_remove_vote_unique_vote_per_option_and_more'),
        ('societies', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 2, 17, 54, 17, 73923, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='poll',
            name='society',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='poll', to='societies.society'),
        ),
    ]
