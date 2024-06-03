# pylint: disable=invalid-str-returned, too-few-public-methods, import-error, too-many-ancestors, no-member, line-too-long # noqa: E501
"""ОРМ приложения system."""
from django.db import models

from django.db.models import Q
from django.core.cache import cache

# from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AbstractUser, UserManager

from django.urls import reverse
from django.utils import timezone
from modules.services.utils import unique_slugify
from phonenumber_field.modelfields import PhoneNumberField


class OfficeNumber(models.Model):
    "Список подразделений РС."
    name = models.CharField("Название участка", max_length=60, blank=True)
    number = models.CharField("Номер участка", max_length=5, blank=True)

    class Meta:
        """Человекочитаемое название модели office_number."""

        verbose_name = "Подразделение РС"
        verbose_name_plural = "Подразделения РС"

    def __str__(self):
        return self.name


class Position(models.Model):
    """Список должностей"""

    name = models.CharField(
        verbose_name="Должность", max_length=255, blank=True
    )  # noqa: E501

    class Meta:
        """Человекочитаемое название модели position."""

        ordering = ["name"]
        verbose_name_plural = "Должности"

    def __str__(self):
        return self.name


class StaffQuerySet(models.QuerySet):
    """Разделение служащих по должностям."""

    def directors(self, office_number):
        """Руководство."""
        return self.filter(
            Q(position=4) | Q(position=5) | Q(position=6)
        ).filter(  # noqa: E501
            office_number=office_number
        )  # noqa: E501

    def surveyors(self):
        """Инспекторы."""
        return self.filter(
            Q(position=1) | Q(position=2) | Q(position=3)
        ).exclude(  # noqa: E501
            is_superuser=True
        )


class StaffManager(models.Manager):
    """Штат филиала."""

    def get_queryset(self):
        """Штат."""
        return StaffQuerySet(self.model, using=self._db)

    def directors(self, office_number):
        """Руководство."""
        return self.get_queryset().directors(office_number)

    def surveyors(self):
        """Инспекторы."""
        return self.get_queryset().surveyors()


class User(AbstractUser):
    """Пользовательская модель user."""

    slug = models.SlugField(
        verbose_name="URL", max_length=255, blank=True, unique=True
    )  # noqa: E501
    patronymic_name = models.CharField("Отчество", max_length=20, blank=True)
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        related_name="users",
        verbose_name=("Должность"),
        null=True,
    )  # noqa: E501
    phone_number = PhoneNumberField("Номер телефона", blank=True)
    proxy_number = models.CharField(
        "Номер доверенности", max_length=20, blank=True
    )  # noqa: E501
    proxy_date = models.DateField("Дата доверенности", null=True, blank=True)
    office_number = models.ForeignKey(
        OfficeNumber,
        on_delete=models.SET_NULL,
        related_name="users",
        verbose_name=("Подразделение"),
        null=True,
    )
    objects = UserManager()
    staff = StaffManager()

    class Meta:
        """
        Сортировка
        """

        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.username)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Возвращение строки
        """
        return self.get_full_name()

    def get_absolute_url(self):
        """
        Ссылка на профиль
        """
        return reverse("profile_detail", kwargs={"slug": self.slug})

    def is_online(self):
        """Проверяет, был ли пользователь онлайн в течение последних 5 минут."""  # noqa: E501
        last_seen = cache.get(f"last-seen-{self.id}")  # type: ignore
        if last_seen is not None and timezone.now() < last_seen + timezone.timedelta(  # type: ignore # noqa: E501
            seconds=300
        ):
            return True
        return False


class Feedback(models.Model):
    """Модель обратной связи."""

    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    email = models.EmailField(
        max_length=255, verbose_name="Электронный адрес (email)", blank=True
    )  # noqa: E501
    content = models.TextField(verbose_name="Содержимое письма")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата отправки"
    )  # noqa: E501
    ip_address = models.GenericIPAddressField(
        verbose_name="IP отправителя", blank=True, null=True
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        """Мета-класс ОРМ обратной связи."""

        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"
        ordering = ["-created_at"]
        db_table = "app_feedback"

    def __str__(self):
        return f"Вам письмо от {self.email}"
