# Generated by Django 4.2.1 on 2024-09-13 11:16

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('apps__campaigns', '0013_campaign_banner_campaign_cta_campaign_template_key_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallToAction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.CharField(blank=True, max_length=100, null=True)),
                ('url', models.URLField()),
            ],
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='cta',
        ),
        migrations.RemoveField(
            model_name='section',
            name='cta',
        ),
        migrations.AddField(
            model_name='campaign',
            name='call_to_action',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apps__campaigns.calltoaction'),
        ),
        migrations.AddField(
            model_name='section',
            name='call_to_actions',
            field=models.ManyToManyField(related_name='section_cta', to='apps__campaigns.calltoaction'),
        ),
    ]
