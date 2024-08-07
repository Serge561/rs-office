# Generated by Django 5.0 on 2024-02-28 20:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0011_alter_employee_position_alter_employee_proxy_number'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='time_create',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='creator',
            new_name='created_by',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='time_update',
            new_name='updated_at',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='updater',
            new_name='updated_by',
        ),
        migrations.AddConstraint(
            model_name='employee',
            constraint=models.UniqueConstraint(fields=('company_id', 'second_name', 'first_name'), name='unique_company_employee'),
        ),
    ]
