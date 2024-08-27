# Generated by Django 4.2.1 on 2024-08-27 12:06

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0154_campaignsupportedlanguage'),
    ]

    operations = [
        migrations.AddField(
            model_name='testimonial',
            name='shared_with',
            field=models.ManyToManyField(blank=True, related_name='shared_testimonials', to='database.community'),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='sharing_type',
            field=models.CharField(choices=[('PUBLIC', 'Public'), ('PRIVATE', 'Private'), ('OPEN_TO', 'Open to'), ('CLOSED_TO', 'Closed to')], default='PUBLIC', max_length=100),
        ),
        migrations.CreateModel(
            name='TestimonialAutoShareSettings',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('info', models.JSONField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('share_from_location_type', models.CharField(choices=[('STATE', 'State'), ('CITY', 'City'), ('ZIPCODE', 'Zipcode'), ('COUNTY', 'County'), ('COUNTRY', 'Country'), ('FULL_ADDRESS', 'Full Address')], default='CITY', max_length=100)),
                ('share_from_location_value', models.CharField(blank=True, max_length=100)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.community')),
                ('excluded_tags', models.ManyToManyField(blank=True, to='database.tag')),
                ('share_from_communities', models.ManyToManyField(blank=True, related_name='share_from_communities', to='database.community')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
