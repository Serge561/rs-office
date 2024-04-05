# Generated by Django 5.0 on 2024-02-11 14:39

import django.db.models.deletion
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0009_alter_bankaccount_options_bankaccount_updated_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('second_name', models.CharField(blank=True, max_length=20, verbose_name='Фамилия')),
                ('first_name', models.CharField(blank=True, max_length=15, verbose_name='Имя')),
                ('patronymic_name', models.CharField(blank=True, max_length=20, verbose_name='Отчество')),
                ('position', models.CharField(blank=True, max_length=55, verbose_name='Должность')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name='Номер телефона')),
                ('extra_number', models.CharField(blank=True, max_length=11, verbose_name='Доб.')),
                ('email', models.EmailField(blank=True, max_length=127, verbose_name='Электронный адрес')),
                ('proxy_type', models.CharField(blank=True, choices=[('CHA', 'Устав'), ('MMC', 'Кодекс торгового мореплавания (КТМ РФ)'), ('PRO', 'Доверенность'), ('ORD', 'Приказ'), ('REG', 'Свидетельство о регистрации')], max_length=3, verbose_name='Действует на основании')),
                ('proxy_number', models.CharField(blank=True, max_length=20, verbose_name='Номер документа')),
                ('proxy_date', models.DateField(blank=True, null=True, verbose_name='Дата доверенности')),
                ('extra_info', models.CharField(blank=True, max_length=127, verbose_name='Доп. информация')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата и время обновления')),
                ('company', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='companies.company', verbose_name='Компания')),
                ('created_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='creator_employees', to=settings.AUTH_USER_MODEL, verbose_name='Создал')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_employees', to=settings.AUTH_USER_MODEL, verbose_name='Обновил')),
            ],
            options={
                'verbose_name': 'Работник компании',
                'verbose_name_plural': 'Персонал компаний',
                'ordering': ['second_name'],
            },
        ),
    ]
