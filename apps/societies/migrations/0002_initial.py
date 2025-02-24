# Generated by Django 5.1.2 on 2025-02-24 00:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('societies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='society',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_societies', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='society',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='societies', to=settings.AUTH_USER_MODEL),
        ),
    ]
