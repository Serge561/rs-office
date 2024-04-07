# pylint: disable=too-few-public-methods, line-too-long, no-member # noqa: E501
"""ОРМ модели account."""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from django.urls import reverse

# from modules.services.mixins import CreatorMixin, UpdaterMixin
from .application import Application


class Account(models.Model):
    """Стоимость услуги."""

    class AccountManager(models.Manager):
        """Менеджер модели account."""

        def all(self):
            """Оптимизация запросов модели account."""
            return self.get_queryset().select_related("application")  # noqa: E501

    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="Номер заявки",
    )
    service_cost = models.DecimalField(
        verbose_name="Стоимость услуги",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(99999999.99)],
        null=True,
    )
    extra_info = models.TextField(
        "Дополнительная информация", max_length=255, blank=True
    )

    objects = AccountManager()

    class Meta:
        """Человекочитаемое название модели account."""

        # ordering = ["id"]
        verbose_name_plural = "Стоимость услуг"

    def __str__(self):
        return f"{self.service_cost}"

    def get_absolute_url(self):
        """Полный URL стоимости услуги."""
        return reverse("account_detail", kwargs={"slug": self.application.company.slug, "pk": self.application.id})  # type: ignore # noqa: E501
