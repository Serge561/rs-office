# Generated by Django 5.0 on 2024-03-10 16:38

import django.contrib.auth.models
import django.db.models.manager
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_alter_user_phone_number'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('staff', django.db.models.manager.Manager()),
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
