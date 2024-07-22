# Generated by Django 4.2.1 on 2024-07-22 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0153_staticsitetext_supportedlanguage_texthash_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translationscache',
            name='hash',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='database.texthash'),
        ),
    ]
