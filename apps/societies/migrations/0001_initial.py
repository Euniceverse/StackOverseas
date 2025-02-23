# Generated by Django 5.1.6 on 2025-02-22 12:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Society',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('society_type', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('request_delete', 'Request Delete'), ('deleted', 'Deleted')], default='pending', max_length=20)),
                ('members_count', models.IntegerField(default=0)),
                ('membership_request_required', models.BooleanField(default=False)),
                ('visibility', models.CharField(choices=[('Private', 'Private'), ('Public', 'Public')], default='Private', max_length=7)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_societies', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(blank=True, related_name='societies', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
