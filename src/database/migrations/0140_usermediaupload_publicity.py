# Generated by Django 3.1.14 on 2023-10-09 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0139_merge_20230921_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermediaupload',
            name='publicity',
            field=models.CharField(default='OPEN_TO', max_length=100),
        ),
    ]
