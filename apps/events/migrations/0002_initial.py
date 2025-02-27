# Generated by Django 5.1.2 on 2025-02-27 13:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        ('societies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='society',
            field=models.ManyToManyField(to='societies.society'),
        ),
        migrations.AddField(
            model_name='eventregistration',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='events.event'),
        ),
    ]
