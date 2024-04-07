# Generated by Django 5.0 on 2024-04-07 16:08

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0007_form_created_at_form_created_by_form_updated_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('application', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='applications.application', verbose_name='Номер заявки')),
                ('service_cost', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(99999999)], verbose_name='Стоимость услуги')),
                ('extra_info', models.TextField(blank=True, max_length=255, verbose_name='Дополнительная информация')),
            ],
            options={
                'verbose_name_plural': 'Стоимость услуг',
            },
        ),
        migrations.AlterField(
            model_name='form',
            name='form_type',
            field=models.CharField(blank=True, choices=[('CER', 'Свидетельство'), ('STA', 'Удостоверение'), ('REP', 'Акт'), ('CHE', 'Чек-лист'), ('ANN', 'Приложение'), ('AGR', 'Соглашение'), ('REG', 'Регистровая книга'), ('REC', 'Журнал'), ('RPT', 'Отчёт'), ('LET', 'Письмо'), ('MIN', 'Протокол'), ('QUR', 'Сообщение'), ('ATL', 'Согласно перечню')], max_length=3, verbose_name='Тип формы'),
        ),
    ]
