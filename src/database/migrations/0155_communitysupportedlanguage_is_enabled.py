# Generated by Django 4.2.1 on 2024-08-14 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0154_campaignsupportedlanguage'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitysupportedlanguage',
            name='is_enabled',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
