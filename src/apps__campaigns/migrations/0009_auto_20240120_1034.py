# Generated by Django 3.2.22 on 2024-01-20 10:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps__campaigns', '0008_technology_more_info_section'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='advert',
        ),
        migrations.RemoveField(
            model_name='campaignconfiguration',
            name='advert',
        ),
        migrations.RemoveField(
            model_name='campaignconfiguration',
            name='navigation',
        ),
        migrations.RemoveField(
            model_name='technology',
            name='icon',
        ),
        migrations.AddField(
            model_name='technology',
            name='campaign_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='campaign_account_technology', to='apps__campaigns.campaignaccount'),
        ),
        migrations.AddField(
            model_name='technology',
            name='help_link',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
