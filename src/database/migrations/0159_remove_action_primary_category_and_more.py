# Generated by Django 4.2.1 on 2025-02-27 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0158_custompage_custompageversion_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='action',
            name='primary_category',
        ),
        migrations.AlterField(
            model_name='communitycustompage',
            name='sharing_type',
            field=models.CharField(choices=[('OPEN', 'OPEN'), ('CLOSED', 'CLOSED'), ('OPEN_TO', 'OPEN_TO'), ('CLOSED_TO', 'CLOSED_TO')], default='OPEN', max_length=100),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='sharing_type',
            field=models.CharField(blank=True, choices=[('OPEN', 'OPEN'), ('CLOSED', 'CLOSED'), ('OPEN_TO', 'OPEN_TO'), ('CLOSED_TO', 'CLOSED_TO')], default='OPEN', max_length=100, null=True),
        ),
    ]
