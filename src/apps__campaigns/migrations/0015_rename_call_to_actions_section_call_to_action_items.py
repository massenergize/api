# Generated by Django 4.2.1 on 2024-09-16 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps__campaigns', '0014_calltoaction_remove_campaign_cta_remove_section_cta_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='section',
            old_name='call_to_actions',
            new_name='call_to_action_items',
        ),
    ]
