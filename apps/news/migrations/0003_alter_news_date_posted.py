# Generated by Django 5.1.6 on 2025-03-26 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='date_posted',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
