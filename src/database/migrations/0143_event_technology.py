# Generated by Django 3.1.14 on 2023-12-07 16:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps__campaigns', '0004_auto_20231207_1621'),
        ('database', '0142_auto_20231103_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='technology',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='apps__campaigns.technology'),
        ),
    ]
