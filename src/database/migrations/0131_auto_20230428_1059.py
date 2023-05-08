# Generated by Django 3.1.14 on 2023-04-28 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0130_policyacceptancerecords'),
    ]

    operations = [
        migrations.RenameField(
            model_name='communitysnapshot',
            old_name='user_count',
            new_name='member_count',
        ),
        migrations.AddField(
            model_name='communitysnapshot',
            name='primary_community_users_count',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]