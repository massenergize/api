# Generated by Django 3.2.4 on 2023-03-16 05:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0127_auto_20230309_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='policyacceptancerecords',
            name='policy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='database.policy'),
        ),
    ]
