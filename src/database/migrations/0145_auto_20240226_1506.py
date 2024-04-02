# Generated by Django 3.2.22 on 2024-02-26 15:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0144_auto_20240221_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventnudgesetting',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventnudgesetting',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]