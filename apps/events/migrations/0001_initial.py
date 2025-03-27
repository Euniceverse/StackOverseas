# Generated by Django 5.1.2 on 2025-03-27 13:03

import datetime
import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=200)),
                ('date', models.DateTimeField()),
                ('start_time', models.TimeField(default=datetime.time(9, 0))),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('event_type', models.CharField(choices=[('sports', 'Sports'), ('academic', 'Academic'), ('arts', 'Arts'), ('cultural', 'Cultural'), ('social', 'Social'), ('other', 'Other')], max_length=50)),
                ('keyword', models.CharField(max_length=50)),
                ('location', models.CharField(max_length=255)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('capacity', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('member_only', models.BooleanField(default=False)),
                ('fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('is_free', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('waitlisted', 'Waitlisted'), ('rejected', 'Rejected')], default='waitlisted', max_length=20)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
