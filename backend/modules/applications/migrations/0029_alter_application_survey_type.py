# Generated by Django 5.0 on 2024-08-29 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0028_alter_document_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='survey_type',
            field=models.CharField(blank=True, choices=[('ISM', 'На соответствие требованиям МКУБ'), ('ISS', 'На соответствие требованиям МК ОСПС'), ('MLC', 'На соответствие требованиям КТМС-2006'), ('DII', 'Рассмотрение II части Декларации о соответствии трудовым нормам в морском судоходстве'), ('OSC', 'Оффшорных контейнеров на соответствие требованиям КБК'), ('TCR', 'Контейнеров-цистерн на соответствие требованиям КБК'), ('EXP', 'Расширение сферы деятельности'), ('CHA', 'Изменение содержания свидетельства'), ('WAC', 'Квалификационные испытания сварщиков'), ('WPS', 'Технологические процессы сварки')], max_length=3, verbose_name='Вид освидетельствования'),
        ),
    ]