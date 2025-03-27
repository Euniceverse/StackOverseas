# Generated by Django 5.1.2 on 2025-03-27 14:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('societies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('widget_type', models.CharField(choices=[('announcements', 'Announcements'), ('gallery', 'Gallery'), ('contacts', 'Contact Information'), ('featured', 'Featured Members'), ('leaderboard', 'Leaderboard'), ('polls', 'Polls'), ('comment', 'Comment')], max_length=50)),
                ('position', models.PositiveIntegerField(default=0)),
                ('custom_html', models.TextField(blank=True, null=True)),
                ('data', models.JSONField(blank=True, null=True)),
                ('society', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='widgets', to='societies.society')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
    ]
