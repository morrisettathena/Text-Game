# Generated by Django 3.0.3 on 2020-05-03 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Engine', '0010_remove_event_hidden_when_inactive'),
    ]

    operations = [
        migrations.AddField(
            model_name='routes',
            name='hidden_when_inactive',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
