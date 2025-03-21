# Generated by Django 5.1.2 on 2025-03-21 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('manager', 'Manager'), ('co_manager', 'Co-Manager'), ('editor', 'Editor'), ('member', 'Member')], default='member', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='MembershipApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answers_json', models.JSONField(blank=True, default=dict)),
                ('essay_text', models.TextField(blank=True)),
                ('portfolio_file', models.FileField(blank=True, null=True, upload_to='society_portfolios/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_rejected', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Society',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('society_type', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('members_count', models.IntegerField(default=0)),
                ('price_range', models.DecimalField(decimal_places=2, default=0.0, max_digits=7)),
                ('membership_request_required', models.BooleanField(default=False)),
                ('visibility', models.CharField(choices=[('Private', 'Private'), ('Public', 'Public')], default='Private', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='SocietyExtraForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_schema', models.JSONField(help_text='JSON representation of the extra form fields.')),
            ],
        ),
        migrations.CreateModel(
            name='SocietyQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=255)),
                ('correct_answer', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='SocietyRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
                ('society_type', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('waitlisted', 'Waitlisted'), ('rejected', 'Rejected')], default='waitlisted', max_length=10)),
                ('extra_form_needed', models.BooleanField(default=False)),
                ('visibility', models.CharField(choices=[('Private', 'Private'), ('Public', 'Public')], default='Private', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='SocietyRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requirement_type', models.CharField(choices=[('none', 'No Extra Requirements'), ('quiz', 'Quiz (Yes/No Questions)'), ('manual', 'Manual Approval (Essay/PDF)')], default='none', max_length=10)),
                ('threshold', models.PositiveIntegerField(default=1, help_text='Minimum number of correct answers required for auto-approval.')),
                ('requires_essay', models.BooleanField(default=False)),
                ('requires_portfolio', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('widget_type', models.CharField(choices=[('announcements', 'Announcements'), ('events', 'Events'), ('gallery', 'Gallery'), ('contacts', 'Contact Information'), ('featured', 'Featured Members'), ('leaderboard', 'Leaderboard'), ('news', 'News')], max_length=50)),
                ('custom_html', models.TextField(blank=True, null=True)),
                ('position', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['position'],
            },
        ),
    ]
