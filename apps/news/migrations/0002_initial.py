# Generated by Django 5.1.2 on 2025-03-21 12:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('news', '0001_initial'),
        ('societies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='society',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='societies.society'),
        ),
    ]
