# Generated by Django 5.0 on 2024-07-02 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0025_alter_application_survey_scope'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='survey_scope',
            field=models.CharField(blank=True, choices=[('I', 'Первоначальное'), ('A', 'Ежегодное'), ('IN', 'Промежуточное'), ('S', 'Очередное'), ('R', 'Возобновляющее'), ('D', 'Подводной части судна'), ('O', 'Внеочередное'), ('C', 'Непрерывное'), ('INT', 'Временное (МКУБ, ОСПС, КТМС)'), ('ADD', 'Дополнительное (МКУБ, ОСПС, КТМС)'), ('PR', 'Первичное (СОДС, СОТПС)'), ('PL', 'Периодическое (СОДС, СОТПС)')], max_length=3, verbose_name='Объём освидетельствования'),
        ),
    ]
