# Generated by Django 4.2.1 on 2025-03-21 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps__campaigns', '0022_campaigncontact_community'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='manager_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='manager_section', to='apps__campaigns.section'),
        ),
    ]
