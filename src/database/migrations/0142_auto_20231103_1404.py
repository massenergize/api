# Generated by Django 3.2 on 2023-11-03 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0141_auto_20231020_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='schedule_info',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='scheduled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
