# Generated by Django 4.2.1 on 2024-08-01 12:56

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0152_menu_contact_info_menu_footer_content'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportedLanguage',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('info', models.JSONField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=5, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('is_right_to_left', models.BooleanField(blank=True, default=False)),
            ],
            options={
                'db_table': 'supported_languages',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='TranslationsCache',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('info', models.JSONField(blank=True, null=True)),
                ('hash', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('source_language_code', models.CharField(max_length=5)),
                ('target_language_code', models.CharField(max_length=5)),
                ('translated_text', models.TextField(max_length=10000)),
                ('last_translated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'translations_cache',
            },
        ),
        migrations.CreateModel(
            name='ManualCommunityTranslation',
            fields=[
                ('translationscache_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='database.translationscache')),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.community')),
            ],
            options={
                'db_table': 'manual_community_translations',
            },
            bases=('database.translationscache',),
        ),
        migrations.CreateModel(
            name='CommunitySupportedLanguage',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('info', models.JSONField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.community')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.supportedlanguage')),
            ],
            options={
                'db_table': 'community_supported_languages',
                'ordering': ('community', 'language'),
                'unique_together': {('community', 'language')},
            },
        ),
    ]