# pylint: disable=too-few-public-methods, invalid-str-returned, import-error, too-many-ancestors, no-member, line-too-long, unsubscriptable-object # noqa: E501
"""ОРМ модели companies."""
import gettext
from django.db import models
from django.urls import reverse

# from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from modules.services.mixins import CreatorMixin, UpdaterMixin
from modules.services.utils import unique_slugify
from modules.system.models import OfficeNumber
from phonenumber_field.modelfields import PhoneNumberField
from localflavor.ru.ru_regions import RU_REGIONS_CHOICES

import pycountry


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


class City(CreatorMixin, UpdaterMixin):
    """Модель городов."""

    class CityManager(models.Manager):
        """Менеджер модели city."""

        def all(self):
            """Оптимизация запросов модели city."""
            return (
                self.get_queryset()
                .select_related("created_by")
                .select_related("updated_by")
            )

    COUNTRIES = [(country.alpha_2, _(country.name)) for country in pycountry.countries]  # type: ignore # noqa: E501

    name = models.CharField("Название", max_length=40, db_index=True)
    country = models.CharField("Страна", choices=COUNTRIES, max_length=2)
    region = models.CharField(
        "Область или край РФ",
        choices=RU_REGIONS_CHOICES,
        blank=True,
    )
    district = models.CharField(
        "Район или городской округ",
        max_length=128,
        blank=True,
    )

    objects = CityManager()

    class Meta:
        """Сортировка."""

        ordering = [
            "name",
        ]
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        """Возвращение строки."""
        if self.region and not self.district:
            return f"{self.name}, {self.get_region_display()}"  # type: ignore # noqa: E501
        if self.region and self.district:
            return f"{self.name}, {self.district}, {self.get_region_display()}"  # type: ignore # noqa: E501
        if not self.region and self.country == "RU":  # type: ignore
            return self.name
        if self.district:
            return f"{self.name}, {self.district}, {self.get_country_display()}"  # type: ignore # noqa: E501
        return f"{self.name}, {self.get_country_display()}"  # type: ignore # noqa: E501


class PlaceMixin(models.Model):
    """Миксин городов со странами и регионами РФ."""

    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        verbose_name="Город",
        null=True,
    )

    class Meta:
        """Определение класса стран и городов как абстрактного."""

        abstract = True


class Company(CreatorMixin, UpdaterMixin):
    """Модель карточки компании."""

    class CompanyManager(models.Manager):
        """Менеджер модели company."""

        def all(self):
            """Оптимизация запросов модели company."""
            return (
                self.get_queryset()
                .select_related("created_by")
                .select_related("updated_by")  # noqa: E501
            )

    name = models.CharField(verbose_name="Название", max_length=255)
    slug = models.SlugField(
        verbose_name="URL", max_length=255, blank=True, unique=True
    )  # noqa: E501
    phone_number = PhoneNumberField("Телефон", blank=True)
    email = models.EmailField("Адрес электронной почты", blank=True)
    inn = models.CharField("ИНН", max_length=12, blank=True)
    kpp = models.CharField("КПП", max_length=9, blank=True)
    ogrn = models.CharField("ОГРН", max_length=15, blank=True)
    responsible_offices = models.ManyToManyField(
        OfficeNumber, verbose_name="Зона деятельности"
    )
    extra_info = models.TextField(
        "Дополнительная информация", max_length=255, blank=True
    )

    objects = CompanyManager()

    class Meta:
        """Meta of companies."""

        # ordering = ["-time_create"]
        ordering = ["-id"]
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Полный URL карточки компании."""
        return reverse("company_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class Address(PlaceMixin, UpdaterMixin):
    """Модель адресов."""

    class AddressManager(models.Manager):
        """Менеджер модели address."""

        def all(self):
            """Оптимизация запросов модели address."""
            return (
                self.get_queryset()
                .select_related("city")
                .select_related("company")
                .select_related("updated_by")  # noqa: E501
            )  # noqa: E501

    class AddressType(models.TextChoices):
        """Выбор типа адреса."""

        POSTAL = "PO", "Почтовый"
        JURIDICAL = "JU", "Юридический"

    company = models.ForeignKey(
        Company,
        verbose_name="Компания",
        on_delete=models.CASCADE,
        related_name="addresses",
        null=True,
    )
    postal_code = models.CharField(
        "Почтовый индекс", max_length=16, blank=True
    )  # noqa: E501
    address_line = models.CharField(
        "Адрес", max_length=256, blank=True, db_index=True
    )  # noqa: E501
    address_type = models.CharField(
        "Тип адреса",
        max_length=2,
        choices=AddressType.choices,
        default=AddressType.POSTAL,
        blank=True,
    )  # type: ignore # noqa: E501
    is_same = models.BooleanField(
        "Фактический адрес совпадает с юридическим", default=True
    )

    objects = AddressManager()

    class Meta:
        """Сортировка."""

        ordering = [
            "id",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "address_type"], name="unique_address"
            )
        ]
        verbose_name = "Адрес компании"
        verbose_name_plural = "Адреса компаний"

    def __str__(self):
        """Возвращение строки."""
        return f"{self.address_line}, {self.city} {self.postal_code}"  # noqa: E501

    def get_absolute_url(self):
        """Полный URL адресов компании."""
        return reverse(
            "company_address_list",
            kwargs={"slug": self.company.slug},  # type: ignore
        )


# ================= Bank ORM =================


class Bank(CreatorMixin, UpdaterMixin):
    """Модель банков."""

    class BankManager(models.Manager):
        """Менеджер модели bank."""

        def all(self):
            """Оптимизация запросов модели bank."""
            return (
                self.get_queryset()
                .select_related("created_by")
                .select_related("updated_by")
            )

    name = models.CharField("Название банка", max_length=128)
    bic = models.CharField(
        "БИК или SWIFT банка/терр. отд. фед. казначейства",
        max_length=11,
        unique=True,  # noqa: E501
    )  # noqa: E501
    correspondent_account = models.CharField(
        "Номер корр. счёта или единого казнач. счёта отделения ЦБР",
        max_length=20,
        blank=True,
    )  # noqa: E501
    regional_treasury_account = models.CharField(
        "Номер казнач. счёта терр. отд. фед. казначейства",
        max_length=20,
        blank=True,
    )  # noqa: E501
    extra_info = models.TextField(
        "Дополнительная информация", max_length=255, blank=True
    )

    objects = BankManager()

    class Meta:
        """Сортировка."""

        ordering = [
            "name",
        ]
        verbose_name = "Банковские реквизиты"
        verbose_name_plural = "Реквизиты банков"

    def __str__(self):
        """Возвращение строки."""
        return self.name


class BankAccount(UpdaterMixin):
    """Модель реквизитов счётов компаний."""

    class BankAccountManager(models.Manager):
        """Менеджер модели bank_account."""

        def all(self):
            """Оптимизация запросов bank_account."""
            return (
                self.get_queryset()
                .select_related("bank")
                .select_related("company")  # noqa: E501
            )  # noqa: E501

    class Currency(models.TextChoices):
        """Валюта счёта."""

        RUB = "RUB", "Российский рубль"
        EUR = "EUR", "Евро"
        USD = "USD", "Доллар США"
        CNY = "CNY", "Китайский юань"
        BYN = "BYN", "Белорусский рубль"

    company = models.ForeignKey(
        Company,
        verbose_name="Компания",
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        null=True,
    )
    bank = models.ForeignKey(
        Bank,
        verbose_name="Банк",
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        null=True,
    )
    bank_account = models.CharField(
        "Расчётный счёт или лицевой счёт в казначействе или IBAN",
        max_length=34,
        # blank=True,
    )  # noqa: E501
    account_currency = models.CharField(
        "Валюта расчётного счёта",
        max_length=3,
        choices=Currency.choices,
        default=Currency.RUB,
        blank=True,
    )
    current_bankaccount = models.BooleanField("Текущий счёт", default=True)

    objects = BankAccountManager()

    class Meta:
        """Сортировка."""

        ordering = [
            "id",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "account_currency"],
                name="unique_bank_account",  # noqa: E501
            )
        ]
        verbose_name = "Реквизиты расчётного счёта компании"
        verbose_name_plural = (
            "Реквизиты банковских/казначейских счетов компаний"  # noqa: E501
        )

    def __str__(self):
        """Возвращение строки."""

        if not self.bank.regional_treasury_account:  # type: ignore
            if self.account_currency == self.Currency.RUB:
                commerce_account_str = f"р/с {self.bank_account}, {self.bank}, БИК {self.bank.bic} к/с {self.bank.correspondent_account}"  # type: ignore # noqa: E501
                return commerce_account_str
            return f"IBAN {self.bank_account}, {self.bank}, BIC {self.bank.bic}"  # type: ignore # noqa: E501
        treasury_account_str = f"сч.№ {self.bank.regional_treasury_account}, {self.bank} ({self.company}, л/с {self.bank_account}), БИК {self.bank.bic} к/с {self.bank.correspondent_account}"  # type: ignore # noqa: E501
        return treasury_account_str

    def get_absolute_url(self):
        """Полный URL счетов компании."""
        return reverse(
            "company_bankaccount_list",
            kwargs={"slug": self.company.slug},  # type: ignore
        )


# ================= Employee ORM =================


class Employee(CreatorMixin, UpdaterMixin):
    """Модель персонала компаний."""

    class EmployeeManager(models.Manager):
        """Менеджер модели employee."""

        def all(self):
            """Оптимизация запросов employee."""
            return self.get_queryset().select_related("company")

        def get_company_staff(self, company):
            """Получить выборку служащих определённой компании."""
            queryset = self.all()
            queryset = queryset.filter(company=company).filter(is_quit=False)
            return queryset

    class ProxyType(models.TextChoices):
        """Выбор вида документа, на основании которого действует лицо."""

        CHARTER = "CHA", "Устав"
        MMCRF = "MMC", "Кодекс торгового мореплавания (КТМ РФ)"
        PROXY = "PRO", "Доверенность"
        ORDER = "ORD", "Приказ"
        REGISTERCERT = "REG", "Свидетельство о регистрации"

    company = models.ForeignKey(
        Company,
        verbose_name="Компания",
        on_delete=models.CASCADE,
        related_name="employees",
        null=True,
    )
    second_name = models.CharField("Фамилия", max_length=20, blank=True)
    first_name = models.CharField("Имя", max_length=15, blank=True)
    patronymic_name = models.CharField("Отчество", max_length=20, blank=True)
    position = models.CharField("Должность", max_length=127, blank=True)
    phone_number = PhoneNumberField("Номер телефона", blank=True)
    extra_number = models.CharField("Доб.", max_length=11, blank=True)
    email = models.EmailField("Электронный адрес", max_length=127, blank=True)
    proxy_type = models.CharField(
        "Действует на основании",
        max_length=3,
        choices=ProxyType.choices,
        blank=True,
    )
    proxy_number = models.CharField(
        "Номер документа", max_length=27, blank=True
    )  # noqa: E501
    proxy_date = models.DateField("Дата доверенности", null=True, blank=True)
    is_quit = models.BooleanField("Не действует", default=False)
    extra_info = models.CharField(
        "Доп. информация", max_length=127, blank=True
    )  # noqa: E501
    objects = EmployeeManager()

    class Meta:
        """Сортировка."""

        ordering = [
            "second_name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "second_name", "first_name"],
                name="unique_company_employee",  # noqa: E501
            )
        ]
        verbose_name = "Работник компании"
        verbose_name_plural = "Персонал компаний"

    def __str__(self):
        """Возвращение строки."""
        return f"{self.second_name} {self.first_name[:1]}. {self.patronymic_name[:1]}."  # noqa: E501

    def get_absolute_url(self):
        """Полный URL профиля работника фирмы."""
        return reverse("employee_detail", kwargs={"slug": self.company.slug, "pk": self.id})  # type: ignore # noqa: E501
