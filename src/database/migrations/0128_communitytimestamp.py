# Generated by Django 3.1.14 on 2023-04-05 15:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0127_auto_20230306_0944'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityTimeStamp',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('is_live', models.BooleanField(blank=True, default=False)),
                ('households_total', models.CharField(max_length=100)),
                ('households_user_reported', models.CharField(max_length=100)),
                ('households_manual_addition', models.CharField(max_length=100)),
                ('households_partner', models.CharField(max_length=100)),
                ('user_count', models.CharField(max_length=100)),
                ('actions_live_count', models.CharField(max_length=100)),
                ('actions_total', models.CharField(max_length=100)),
                ('actions_partner', models.CharField(max_length=100)),
                ('actions_user_reported', models.CharField(max_length=100)),
                ('events_hosted', models.CharField(max_length=100)),
                ('placeholder_events_shared', models.CharField(blank=True, max_length=100)),
                ('placeholder_events_at_large', models.CharField(blank=True, max_length=100)),
                ('carbon_total', models.CharField(max_length=100)),
                ('carbon_user_reported', models.CharField(max_length=100)),
                ('carbon_manual_addition', models.CharField(max_length=100)),
                ('carbon_partner', models.CharField(max_length=100)),
                ('not_live_actions', models.CharField(max_length=100)),
                ('not_live_events', models.CharField(max_length=100)),
                ('community', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='database.community')),
            ],
            options={
                'db_table': 'community_time_stamps',
            },
        ),
    ]