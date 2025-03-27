# Generated by Django 5.1.6 on 2025-03-27 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widgets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widget',
            name='widget_type',
            field=models.CharField(choices=[('announcements', 'Announcements'), ('gallery', 'Gallery'), ('contacts', 'Contact Information'), ('featured', 'Featured Members'), ('leaderboard', 'Leaderboard'), ('polls', 'Polls'), ('comment', 'Comment')], max_length=50),
        ),
    ]
