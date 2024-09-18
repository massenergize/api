# Generated by Django 4.2.1 on 2024-09-18 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps__campaigns', '0015_rename_call_to_actions_section_call_to_action_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='banner_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='banner_section', to='apps__campaigns.section'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='featured_summary',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='technology',
            name='summary',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
