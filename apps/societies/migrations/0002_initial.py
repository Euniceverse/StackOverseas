

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
            model_name='membership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_memberships', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='membershipapplication',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='society_applications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='society',
            name='manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_societies', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='society',
            name='members',

            field=models.ManyToManyField(blank=True, related_name='societies_joined', through='societies.Membership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='membershipapplication',
            name='society',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='societies.society'),
        ),
        migrations.AddField(
            model_name='membership',
            name='society',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='society_memberships', to='societies.society'),
        ),
        migrations.AddField(
            model_name='societyrequirement',
            name='society',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='requirement', to='societies.society'),
        ),
        migrations.AddField(
            model_name='societyquestion',
            name='society_requirement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='societies.societyrequirement'),

        ),
    ]
