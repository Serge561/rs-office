# Generated by Django 5.0 on 2024-03-31 14:36

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0006_document_application_document_form_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="form",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Дата и время создания",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="form",
            name="created_by",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="%(app_label)s_%(class)s_related_cr",
                related_query_name="%(app_label)s_%(class)ss_cr",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Создал",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True, null=True, verbose_name="Дата и время обновления"
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(app_label)s_%(class)s_related_u",
                related_query_name="%(app_label)s_%(class)ss_u",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Обновил",
            ),
        ),
        migrations.AlterField(
            model_name="application",
            name="occasional_cause",
            field=models.TextField(
                blank=True,
                max_length=127,
                verbose_name="Причина внеочередного освидетельствования и уточнение информации по другим кодам",
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="form",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="applications.form",
                verbose_name="Вид и номер формы документа",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="document",
            name="number",
            field=models.CharField(
                max_length=20, verbose_name="Номер документа или письма об одобрении ТД"
            ),
        ),
    ]
