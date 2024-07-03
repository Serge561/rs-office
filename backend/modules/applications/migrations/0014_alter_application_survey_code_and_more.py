# Generated by Django 5.0 on 2024-06-20 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0013_alter_vesselextrainfo_class_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='survey_code',
            field=models.CharField(choices=[('Classification survey of ships in service', 'Классификационные освидетельствования судов в эксплуатации'), ('Technical supervision for shipbuilding', 'Техническое наблюдение за постройкой судна'), ('Services on survey of a ship in repair', 'Услуги по освидетельствованию судна в ремонте'), ('Technical supervision for production of materials and products not shipborne purpose', 'Техническое наблюдение за изготовлением материалов и изделий не судового назначения'), ('Technical supervision for production of steel', 'Техническое наблюдение за изготовлением стали'), ('Review of technical documentation', 'Рассмотрение технической документации'), ('Tonnage', 'Обмер судов'), ('IACS substitution', 'Замещение ИКО'), ('Technical supervision for containers', 'Техническое наблюдение за контейнерами'), ('Other types of activity', 'Прочие виды деятельности'), ('Survey on compliance with ISM ISPS MLC of ships', 'Освидетельствование на соответствие МКУБ, ОСПС, КТМС судов'), ('Survey on compliance with other ICs for ships in service', 'Освидетельствование на соответствие другим МК судов в эксплуатации'), ('Voluntary certification', 'Добровольная сертификация'), ('Survey on compliance with ISMC for shipborne companies', 'Освидетельствование на соответствие МКУБ судовых компаний'), ('Technical supervision for production of materials and products for ships', 'Техническое наблюдение за изготовлением материалов и изделий для судов'), ('Technical supervision for FMPs and pipelines building', 'Техническое наблюдение за постройкой МСП и трубопроводов'), ('Safety management system certification', 'Сертификация систем менеджмента качества'), ('Classification tests of welders and approval of welding procedure specifications (WAC and WPSAC)', 'Квалификационные испытания сварщиков и одобрение технологических процессов сварки (СОДС, СОТПС)'), ('Product certification in GOST R system', 'Сертификация продукции в системе ГОСТ Р'), ('Survey of firms and laboratories on the Russian territory (RC CFC RCOM TLC)', 'Освидетельствование предприятий, лабораторий на территории России (СП, ССП, СПИ, СПЛ)'), ('Survey of firms and laboratories on a territory of other countries (not Russia)', 'Освидетельствование предприятий, лабораторий на территории других стран (не Россия)'), ('Services on declaration and certification of bulk and dangerous cargoes, certification of containers', 'Услуги по декларированию и сертификации навалочных и опасных грузов, сертификация тары'), ('Technical supervision according to a firm report (with VAT)', 'Техническое наблюдение согласно отчёту предприятия (с НДС)'), ('Classification and survey of a small craft', 'Классификация и освидетельствование маломерного судна')], default='Classification survey of ships in service', max_length=100, verbose_name='Код услуги'),
        ),
        migrations.AlterField(
            model_name='application',
            name='survey_object',
            field=models.CharField(blank=True, choices=[('Ship', 'Судно'), ('Ship on the all parts', 'Судно по всем частям'), ('Ship on the hull part', 'Судно по корпусной части'), ('Ship on the mechanical part', 'Судно по механической части'), ('Ship on the electric-mechanical parts', 'Судно по электромеханической части'), ('Ship on the hull and mechanical parts', 'Судно по корпусной и механической частям'), ('Ship on the mechanical and electric-mechanical parts', 'Судно по механической и электромеханической частям')], default='ALLO', max_length=52, verbose_name='Объекты освидетельствования'),
        ),
        migrations.AlterField(
            model_name='application',
            name='survey_scope',
            field=models.CharField(blank=True, choices=[('Initial', 'Первоначальное'), ('Annual', 'Ежегодное'), ('Intermediate', 'Промежуточное'), ('Special', 'Очередное'), ('Renewal', 'Возобновляющее'), ('Bottom', 'Подводной части судна'), ('Occasional', 'Внеочередное'), ('Continuous', 'Непрерывное'), ('Interim (ISM ISPS MLC)', 'Временное (МКУБ, ОСПС, КТМС)'), ('Additional (ISM ISPS MLC)', 'Дополнительное (МКУБ, ОСПС, КТМС)'), ('Primary (WAC WPSAC)', 'Первичное (СОДС, СОТПС)'), ('Periodical (WAC WPSAC)', 'Периодическое (СОДС, СОТПС)')], max_length=25, verbose_name='Объём освидетельствования'),
        ),
        migrations.AlterField(
            model_name='application',
            name='survey_type',
            field=models.CharField(blank=True, choices=[('On compliance with the requirements of ISMC', 'На соответствие требованиям МКУБ'), ('On compliance with the requirements of ISPS IC', 'На соответствие требованиям МК ОСПС'), ('On compliance with the requirements of MLC-2006 Convention', 'На соответствие требованиям КТМС-2006'), ('Review of Declaration of Maritime Labour Compliance part II', 'Рассмотрение II части Декларации о соответствии трудовым нормам в морском судоходстве'), ('Expanding field of activity', 'Расширение сферы деятельности'), ('Changing content of the certificate', 'Изменение содержания свидетельства'), ('Welder approvals', 'Квалификационные испытания сварщиков'), ('Welding procedure specifications', 'Технологические процессы сварки')], max_length=60, verbose_name='Вид освидетельствования'),
        ),
    ]
