# Generated by Django 2.2.3 on 2019-07-18 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0003_graph_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagesection',
            name='description',
            field=models.TextField(blank=True, max_length=10000),
        ),
        migrations.AddField(
            model_name='pagesection',
            name='title',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='pagesection',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
