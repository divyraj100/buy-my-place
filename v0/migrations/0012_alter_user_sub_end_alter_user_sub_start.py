# Generated by Django 5.0.1 on 2024-04-02 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v0', '0011_alter_user_sub_end_alter_user_sub_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='sub_end',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='sub_start',
            field=models.DateField(default=None, null=True),
        ),
    ]
