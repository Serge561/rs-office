# pylint: disable=line-too-long, too-many-ancestors, too-few-public-methods, import-error # noqa: E501
"""ОРМ модели application."""

import gettext
import pycountry
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from modules.services.mixins import CreatorMixin, UpdaterMixin

User = get_user_model()


class CharNullField(models.CharField):
    """CharField поле которое конвертирует пустую строку в NULL."""

    # description = "CharField that stores NULL"
    def get_db_prep_value(self, value, connection=None, prepared=False):
        """Функция конвертации пустой строки в NULL."""
        value = super().get_db_prep_value(value, connection, prepared)
        if value == "":
            return None
        return value


russian = gettext.translation(
    "iso3166-1", pycountry.LOCALES_DIR, languages=["ru"]
)  # noqa: E501
russian.install()
_ = russian.gettext


class Vessel(CreatorMixin, UpdaterMixin):
    """Модель судов."""

    class VesselManager(models.Manager):
        """Менеджер модели vessel."""

        def all(self):
            """Оптимизация запросов модели vessel."""
            return (
                self.get_queryset()
                .select_related("created_by")
                .select_related("updated_by")
            )

    COUNTRIES = [(country.alpha_2, _(country.name)) for country in pycountry.countries]  # type: ignore # noqa: E501

    class VesselStatGroup(models.TextChoices):
        """Выбор статистической группы судов."""

        OILTANKER = "OIL", "Нефтеналивные"
        OILCHEMTANKER = "OCT", "Нефтеналивные/Химовозы"
        CHEMTANKER = "CHE", "Химовозы"
        GASCARRIER = "GAS", "Газовозы"
        OTHERTANKER = "OTH", "Наливные прочие"
        OILORECARRIER = "OOC", "Нефтенавалочные и нефтерудовозы"
        ORECARRBULKER = "OCB", "Рудовозы и навалочные"
        GENERALCARGO = "GEN", "Суда для генгруза"
        CARGOPASSANGER = "CPA", "Грузопассажирские"
        CONTAINERSHIP = "CON", "Контейнерные, баржевозы, доковые"
        CARCARRIER = "CAR", "Суда для перевозки транспортных средств"
        FISHTRANSPORT = "FTV", "Рыбопромысловые базы, рыботранспортные суда"
        FISHINGVESSEL = "FIS", "Рыболовные"
        PASSANGERSHIP = "PAS", "Пассажирские и пассажирские бескоечные"
        SUPPLER = "SUP", "Суда обеспечения, обслуживающие суда"
        TUG = "TUG", "Буксиры"
        DRADGER = "DRA", "Земснаряды"
        REEFER = "REF", "Рефрижераторные"
        ICEBRAKER = "ICE", "Ледоколы"
        RESEARCHSHIP = "RES", "Научно-исследовательские"
        OTHERSHIP = "OTS", "Прочие суда"
        SMALLCRAFT = "SMC", "Маломерные/прогулочные"
        PIPELINE = "PIP", "Трубопроводы/ПДК"

    name = models.CharField("Название судна", max_length=55)
    name_en = models.CharField(
        "Транслитерация названия судна", max_length=55, blank=True
    )
    rs_number = CharNullField(
        "Регистровый номер", max_length=6, unique=True, null=True, blank=True
    )
    imo_number = CharNullField(
        "Номер ИМО", max_length=7, unique=True, null=True, blank=True
    )  # noqa: E501
    g_tonnage = models.PositiveIntegerField(
        "Валовая вместимость", null=True, blank=True
    )
    build_date = models.DateField("Дата постройки", null=True, blank=True)
    me_power = models.PositiveIntegerField(
        "Мощность ГД", null=True, blank=True
    )  # noqa: E501
    flag = models.CharField("Флаг судна", choices=COUNTRIES, max_length=2)
    vessel_stat_group = models.CharField(
        "Статистическая группа судна",
        max_length=3,
        choices=VesselStatGroup.choices,
        blank=True,
    )
    is_international_voyage = models.BooleanField(
        "Совершает международные рейсы", default=True
    )

    objects = VesselManager()

    class Meta:
        """Сортировка."""

        ordering = [
            "name",
        ]
        verbose_name = "Судно"
        verbose_name_plural = "Суда"

    def __str__(self):
        """Возвращение строки."""
        return f'"{self.name}" РС {self.rs_number}'

    def get_absolute_url(self):
        """Полный URL характеристик судна."""
        return reverse("vessel_detail", kwargs={"pk": self.id})  # type: ignore # noqa: E501
