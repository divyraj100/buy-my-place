# Generated by Django 5.0.2 on 2024-02-29 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v0', '0005_user_is_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='otp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
