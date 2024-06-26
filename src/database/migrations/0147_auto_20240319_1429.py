# Generated by Django 3.2.22 on 2024-03-19 14:29

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0146_auto_20240227_1258'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureflag',
            name='allow_opt_in',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.CreateModel(
            name='CommunityNotificationSetting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('notification_type', models.CharField(choices=[('user-event-nudge-feature-flag', 'user-event-nudge-feature-flag')], max_length=100)),
                ('is_active', models.BooleanField(blank=True, default=True)),
                ('activate_on', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('more_info', models.JSONField(blank=True, null=True)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_settings', related_query_name='notification_setting', to='database.community')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='database.userprofile')),
            ],
        ),
    ]
