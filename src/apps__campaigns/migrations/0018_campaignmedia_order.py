# Generated by Django 4.2.1 on 2024-09-30 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps__campaigns', '0017_campaignmedia'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaignmedia',
            name='order',
            field=models.PositiveIntegerField(default=1),
        ),
    ]