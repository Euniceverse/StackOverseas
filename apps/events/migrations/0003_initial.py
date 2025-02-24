# Generated by Django 5.1.2 on 2025-02-24 15:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0002_initial'),
        ('societies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='eventregistration',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_registrations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='host',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event'),
        ),
        migrations.AddField(
            model_name='host',
            name='society',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='societies.society'),
        ),
    ]
