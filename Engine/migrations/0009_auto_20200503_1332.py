# Generated by Django 3.0.3 on 2020-05-03 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Engine', '0008_response_hidden_when_inactive'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='hidden_when_inactive',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='response',
            name='hidden_when_inactive',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
