# Generated by Django 4.2.1 on 2024-06-20 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0151_rename_is_default_menu_is_custom'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='contact_info',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='menu',
            name='footer_content',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
