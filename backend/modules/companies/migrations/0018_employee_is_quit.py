# Generated by Django 5.0 on 2024-06-11 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0017_alter_bank_correspondent_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_quit',
            field=models.BooleanField(default=False, verbose_name='Не действует'),
        ),
    ]
