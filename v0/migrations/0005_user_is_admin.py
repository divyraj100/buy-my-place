# Generated by Django 5.0.1 on 2024-02-23 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v0', '0004_conus'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
