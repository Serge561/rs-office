# Generated by Django 5.0 on 2024-02-28 20:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0012_rename_time_create_company_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='employee',
            name='unique_company_employee',
        ),
    ]
