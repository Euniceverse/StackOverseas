# Generated by Django 5.1.2 on 2025-02-21 15:19

import datetime
import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('societies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
                ('capacity', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('member_only', models.BooleanField(default=False)),
                ('fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('is_free', models.BooleanField(default=True)),
                ('society', models.ManyToManyField(to='societies.society')),
            ],
        ),
        migrations.CreateModel(
            name='EventRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('waitlisted', 'Waitlisted'), ('rejected', 'Rejected')], default='waitlisted', max_length=20)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_registrations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('society', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='societies.society')),
            ],
        ),
    ]
