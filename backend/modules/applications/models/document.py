# pylint: disable=line-too-long, too-many-ancestors, too-few-public-methods, import-error, invalid-str-returned, no-member # noqa: E501
"""ОРМ модели document."""

from django.db import models
from django.urls import reverse
from modules.services.mixins import CreatorMixin, UpdaterMixin
from .application import Application


class Form(CreatorMixin, UpdaterMixin):
    """Формы документов."""

    class FormManager(models.Manager):
        """Менеджер модели vessel."""

        def all(self):
            """Оптимизация запросов модели form."""
            return (
                self.get_queryset()
                .select_related("created_by")
                .select_related("updated_by")
            )

    class FormType(models.TextChoices):
        """Выбор типа формы."""

        ATL = "ATL", "Согласно перечню"
        RPT = "RPT", "Отчёт"
        CER = "CER", "Свидетельство"
        STA = "STA", "Удостоверение"
        REP = "REP", "Акт"
        LET = "LET", "Письмо об одобрении"
        AGT = "AGN", "Договор"
        CHE = "CHE", "Чек-лист"
        ANN = "ANN", "Приложение"
        AGR = "AGR", "Соглашение"
        REG = "REG", "Регистровая книга"
        REC = "REC", "Журнал"
        MIN = "MIN", "Протокол"
        QUR = "QUR", "Сообщение"

    number = models.CharField(
        verbose_name="Номер формы", max_length=20, blank=True
    )  # noqa: E501
    form_type = models.CharField(
        "Тип формы",
        max_length=3,
        choices=FormType.choices,
        blank=True,
    )
    description = models.CharField(
        verbose_name="Описание формы", max_length=255, blank=True
    )

    objects = FormManager()

    class Meta:
        """Человекочитаемое название модели form."""

        ordering = ["number"]
        verbose_name_plural = "Формы документов"

    def __str__(self):
        if self.form_type not in [self.FormType.LET, self.FormType.AGT]:
            return f"{self.get_form_type_display()} ф. {self.number}"  # type: ignore # noqa: E501
        return f"{self.number} №"  # type: ignore # noqa: E501


class Document(models.Model):
    """Выданные документы."""

    class DocumentManager(models.Manager):
        """Менеджер модели document."""

        def all(self):
            """Оптимизация запросов модели document."""
            return (
                self.get_queryset()
                .select_related("form")
                .select_related("application")  # noqa: E501
            )

    application = models.ForeignKey(
        to=Application,
        verbose_name="Номер заявки",
        on_delete=models.CASCADE,
        related_name="documents",
        blank=True,
        null=True,
    )
    number = models.CharField(
        verbose_name="Номер документа, письма об одобрении ТД или договора",
        max_length=30,  # , blank=True
    )  # noqa: E501
    form = models.ForeignKey(
        to=Form,
        verbose_name="Вид и номер формы документа",
        on_delete=models.CASCADE,
        related_name="documents",
        blank=True,
        null=True,
    )
    item_particulars = models.TextField(
        "Описание услуги по освид. материалов и изделий",
        blank=True,
    )

    objects = DocumentManager()

    class Meta:
        """Человекочитаемое название модели document."""

        ordering = ["number"]
        verbose_name_plural = "Выданные документы"

    def __str__(self):
        return self.number

    def get_absolute_url(self):
        """Полный URL документа."""
        return reverse("document_detail", kwargs={"slug": self.application.company.slug, "pk": self.application.pk, "id": self.id})  # type: ignore # noqa: E501
