# Generated by Django 5.1.6 on 2025-02-28 12:09

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
        migrations.AddField(
            model_name='societyregistration',
            name='applicant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='society_applications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='societyregistration',
            name='extra_form',
            field=models.OneToOneField(blank=True, help_text='Reference to the extra form for society registration.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registration', to='societies.societyextraform'),
        ),
        migrations.AddField(
            model_name='societyextraform',
            name='society_registration',
            field=models.OneToOneField(help_text='Custom form for society membership applications.', on_delete=django.db.models.deletion.CASCADE, related_name='extra_form_entry', to='societies.societyregistration'),
        ),
        migrations.AddField(
            model_name='widget',
            name='society',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='widgets', to='societies.society'),
        ),
    ]
