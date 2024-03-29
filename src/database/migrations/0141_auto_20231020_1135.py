# Generated by Django 3.1.14 on 2023-10-20 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0140_usermediaupload_publicity'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='hash',
            field=models.TextField(blank=True, db_index=True, max_length=10000),
        ),
        migrations.AlterField(
            model_name='usermediaupload',
            name='publicity',
            field=models.CharField(blank=True, default='OPEN_TO', max_length=100, null=True),
        ),
    ]
