# Generated by Django 5.0 on 2024-02-03 21:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_address_unique_address'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='Название банка')),
                ('bic', models.CharField(blank=True, max_length=16, verbose_name='БИК банка')),
                ('correspondent_account', models.CharField(blank=True, max_length=20, verbose_name='Номер коррсчёта')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата и время обновления')),
                ('created_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='creator_banks', to=settings.AUTH_USER_MODEL, verbose_name='Создал')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_banks', to=settings.AUTH_USER_MODEL, verbose_name='Обновил')),
            ],
            options={
                'verbose_name': 'Банковские реквизиты',
                'verbose_name_plural': 'Реквизиты банков',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_account', models.CharField(blank=True, max_length=20, verbose_name='Расчётный счёт')),
                ('account_currency', models.CharField(blank=True, choices=[('RUB', 'Российский рубль'), ('EUR', 'Евро'), ('USD', 'Доллар США'), ('CNY', 'Китайский юань'), ('BYN', 'Белорусский рубль')], default='RUB', max_length=3, verbose_name='Валюта расчётного счёта.')),
                ('bank', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bank_accounts', to='companies.bank', verbose_name='Банк')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bank_accounts', to='companies.company', verbose_name='Компания')),
            ],
            options={
                'verbose_name': 'Реквизиты расчётного счёта компании',
                'verbose_name_plural': 'Реквизиты расчётных счетов компаний',
                'ordering': ['id'],
            },
        ),
        migrations.AddConstraint(
            model_name='bankaccount',
            constraint=models.UniqueConstraint(fields=('company_id', 'account_currency'), name='unique_account'),
        ),
    ]
