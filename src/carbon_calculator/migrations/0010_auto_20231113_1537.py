# Generated by Django 3.2 on 2023-11-13 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carbon_calculator', '0009_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40, unique=True)),
                ('is_deleted', models.BooleanField(blank=True, default=False)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'db_table': 'categories_cc',
            },
        ),
        migrations.RenameField(
            model_name='action',
            old_name='category',
            new_name='old_category',
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('is_deleted', models.BooleanField(blank=True, default=False)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carbon_calculator.category')),
            ],
            options={
                'db_table': 'subcategories_cc',
            },
        ),
    ]