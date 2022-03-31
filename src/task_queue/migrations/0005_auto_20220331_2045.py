# Generated by Django 3.1.14 on 2022-03-31 20:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0116_auto_20220305_1557'),
        ('django_celery_beat', '0015_edit_solarschedule_events_choices'),
        ('task_queue', '0004_auto_20220331_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_queue_creator', to='database.userprofile'),
        ),
        migrations.AlterField(
            model_name='task',
            name='schedule',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_queue_schedule', to='django_celery_beat.periodictask'),
        ),
    ]
