# Generated by Django 5.1.2 on 2025-03-27 14:23

import apps.news.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('date_posted', models.DateTimeField(blank=True, null=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=apps.news.models.upload_to)),
                ('is_published', models.BooleanField(default=False)),
                ('views', models.PositiveIntegerField(default=0)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='news_articles', to='events.event')),
            ],
            options={
                'ordering': ['-date_posted'],
            },
        ),
    ]
