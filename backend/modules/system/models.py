# pylint: disable=invalid-str-returned, too-few-public-methods, import-error, too-many-ancestors # noqa: E501
"""ОРМ приложения system."""
from django.db import models

from django.db.models import Q

# from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AbstractUser, UserManager
from django.urls import reverse
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
        return self.filter(Q(position=1) | Q(position=2) | Q(position=3))


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


# User.objects.filter(username__icontains = "user")
# >>> User.objects.filter(
# ... username__startswith='user'
# ... ).filter(
# ... date_joined__gte=datetime.date.today()
# ... ).exclude(
# ... is_active=False
# ... )

# from django.db.models import Q

# User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
# User.objects.filter(username__icontains = "user")
