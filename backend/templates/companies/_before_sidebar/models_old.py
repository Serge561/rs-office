# pylint: disable=too-few-public-methods, invalid-str-returned, import-error, too-many-ancestors, no-member, line-too-long # noqa: E501
"""ОРМ модели application."""

import gettext
from django.db import models

# from django.urls import reverse

# from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

# from modules.services.utils import unique_slugify
# from modules.system.models import OfficeNumber

import pycountry

from modules.companies.models import Company, Employee, PlaceMixin


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


class Vessel(models.Model):
    """Модель судов."""

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

    class ClassStatus(models.TextChoices):
        """Выбор состояния класса судна."""

        INBUILDING = "01", "Судно в постройке на класс РС"
        INSERVCLAS = (
            "02",
            "Судно в эксплуатации в стадии присвоения класса РС",
        )  # noqa: E501
        INSIACSTAD = (
            "03",
            "Судно в эксплуатации с классом ИКО в стадии выдачи РС конвенционных документов",  # noqa: E501
        )  # noqa: E501
        INSRCOSTAD = (
            "04",
            "Судно в эксплуатации с классом РКО и флагом РФ в стадии выдачи РС конвенционных документов",  # noqa: E501
        )  # noqa: E501
        SUPVISUSPD = (
            "06",
            "Техническое наблюдение за постройкой судна приостановлено",
        )  # noqa: E501
        APPLICWDRN = "07", "Заявка аннулирована"
        BUIDCEASED = "08", "Строительство прекращено"
        BUILDSUSPD = (
            "09",
            "Постройка законсервирована, освидетельствование не выполняется",
        )  # noqa: E501
        BUILDINTED = (
            "10",
            "Судно предполагается к строительству на класс РС",
        )  # noqa: E501
        INSERVICE = "11", "Класс действует (в эксплуатации)"
        INREPAIR = "12", "В ремонте"
        LAIDUP = "13", "Класс действует (в отстое)"
        RESERVED = "14", "Резервный код"
        INSFORSEMR = "15", "Класс действует (форс-мажор)"
        INSURVEY = (
            "16",
            "Класс действует (судно в процессе освидетельствования)",
        )
        SUSPDAMAGE = "21", "Класс приостановлен (аварийный случай)"
        SUSPOVRDUE = (
            "22",
            "Класс приостановлен (просрочено освидетельствование)",
        )
        SUSPENVELP = "23", "Класс приостановлен (судно в консервации)"
        SUSPLUPOVD = (
            "24",
            "Класс приостановлен в отстое (просрочено освидетельствование)",
        )
        SUSPLAIDUP = (
            "25",
            "Класс приостановлен (судно выведено в отстой с приостановленным классом)",  # noqa: E501
        )
        SUSPREQOVD = (
            "26",
            "Класс приостановлен (невыполнение требований или условий сохранения класса)",  # noqa: E501
        )
        SUSPOTHERS = (
            "27",
            "Класс приостановлен (причины, не связаные с безопасностью)",
        )
        SUSPINSURV = (
            "28",
            "Класс приостановлен (судно в процессе освидетельствования для восстановления класса)",  # noqa: E501
        )
        WDRANOWNER = "31", "Класс снят (просьба судовладельца)"
        WDRANPASSD = (
            "32",
            "Класс снят (истекли 6 месяцев после приостановки класса)",
        )
        WDRANRULES = "33", "Класс снят (невыполнение требований Правил РС)"
        WDRANOTHER = "34", "Класс снят (причины, не связаные с безопасностью)"
        WDRANSCAPD = (
            "41",
            "Класс снят (разделано или продано для разделки на металлолом)",
        )
        WDRANWRECK = "42", "Класс снят (гибель)"
        WDRANDAMAG = "43", "Класс снят (аварийный случай)"
        INSREINSTD = "51", "Класс действует (восстановлен после приостановки)"
        INSREASSIG = "52", "Класс действует (переназначен после снятия)"
        INSTRANSIA = (
            "61",
            "Класс действует (принято в класс РС из класса общества-члена МАКО)",  # noqa: E501
        )
        INSTRNONIA = (
            "62",
            "Класс действует (принято в класс РС из класса общества-не члена МАКО)",  # noqa: E501
        )
        WDRANTOIAC = (
            "71",
            "Класс снят (переход из класса РС в класс общества-члена МАКО)",
        )
        WDRANTONIA = (
            "72",
            "Класс снят (переход из класса РС в класс общества-не члена МАКО)",
        )
        SMCRINSERV = "80", "Маломерное прогулочное судно в эксплуатации"
        SMCRNOTINS = "90", "Маломерное прогулочное судно не в эксплуатации"
        IACSCLASS = "99", "Класс ИКО"

    name = models.CharField("Название судна", max_length=55)
    name_en = models.CharField("Vessel's name", max_length=55, blank=True)
    rs_number = models.CharField(
        "Регистровый номер", max_length=6, unique=True, blank=True
    )
    imo_number = models.CharField(
        "Номер ИМО", max_length=7, unique=True, blank=True
    )  # noqa: E501
    g_tonnage = models.PositiveIntegerField(
        "Валовая вместимость", null=True, blank=True
    )
    build_date = models.DateField("Дата постройки", null=True, blank=True)
    me_power = models.PositiveSmallIntegerField(
        "Мощность ГД", null=True, blank=True
    )  # noqa: E501
    flag = models.CharField("Страна", choices=COUNTRIES, max_length=2)
    vessel_stat_group = models.CharField(
        "Статистическая группа судна",
        max_length=3,
        choices=VesselStatGroup.choices,
        blank=True,
    )
    is_international_voyage = models.BooleanField(
        "Совершает международные рейсы", default=True
    )
    class_status = models.CharField(
        "Текущий статус состояния класса судна",
        choices=ClassStatus.choices,
        max_length=2,  # noqa: E501
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время создания"
    )  # noqa: E501
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата и время обновления",
        null=True,
        blank=True,  # noqa: E501
    )  # noqa: E501
    created_by = models.ForeignKey(
        to=User,
        verbose_name="Создал",
        on_delete=models.SET_DEFAULT,
        related_name="creator_vessels",
        default=None,
        null=True,
    )
    updated_by = models.ForeignKey(
        to=User,
        verbose_name="Обновил",
        on_delete=models.SET_NULL,
        null=True,
        related_name="updater_vessels",
        blank=True,
    )

    class Meta:
        """Сортировка."""

        ordering = [
            "name",
        ]
        verbose_name = "Судно"
        verbose_name_plural = "Суда"

    def __str__(self):
        """Возвращение строки."""
        return f"{self.name} РС {self.rs_number}"


class Application(PlaceMixin):
    """Модель заявок."""

    class ApplicationManager(models.Manager):
        """Менеджер модели address."""

        def all(self):
            """Оптимизация запросов модели address."""
            return (
                self.get_queryset()
                .prefetch_related("assigned_surveyors")
                .select_related("city")
                .select_related("company")
                .select_related("vessel")
                .select_related("register_signer")
                .select_related("applicant_signer")
                .select_related("authorized_person")
                .select_related("created_by")
                .select_related("updated_by")
            )  # noqa: E501

    class SurveyCode(models.TextChoices):
        """Выбор кода услуги."""

    # 00001	Классификационные освидетельствования судов в эксплуатации
    # 00002	Техническое наблюдение за постройкой судна
    # 00003	Услуги по освидетельствованию судна в ремонте
    # 00004	Техническое наблюдение за изготовлением материалов и изделий не судового назначения   # noqa: E501
    # 00005	Техническое наблюдение за изготовлением стали
    # 00006	Рассмотрение технической документации
    # 00007	Обмер судов
    # 00008	Замещение ИКО
    # 00009	Техническое наблюдение за контейнерами
    # 00010	Прочие виды деятельности
    # 00011	Освидетельствование на соответствие МКУБ, ОСПС, КТМС судов
    # 00012	Освидетельствование на сответствие другим МК судов в эксплуатации
    # 00013	Добровольная сертификация
    # 00014	Освидетельствование на соответствие МКУБ судовых компаний
    # 00015	Техническое наблюдение за изготовлением материалов и изделий для судов   # noqa: E501
    # 00016	Техническое наблюдение за постройкой МСП и трубопроводов
    # 00100	Сертификация систем менеджмента качества
    # 00101	Квалификационные испытания сварщиков и одобрение технологических процессов сварки (СДС, СПС)   # noqa: E501
    # 00102	Сертификация продукции в системе ГОСТ Р
    # 00103	Освидетельствование предприятий, лабораторий на территории России (СП, ССП, СПИ, СПЛ)   # noqa: E501
    # 00104	Освидетельствование предприятий, лабораторий на территории других стран (не Россия)   # noqa: E501
    # 00105	Услуги по декларированию и сертификации навалочных и опасных грузов, сертификация тары   # noqa: E501
    # 0015*	Техническое наблюдение согласно отчёту предприятия (без НДС)
    # 0103*	Техническое наблюдение согласно отчёту предприятия (с НДС)

    class SurveyType(models.TextChoices):
        """Выбор вида освидетельствования."""

    # Вид освидетельствования (рус.)
    # на соответствие требованиям МКУБ
    # системы охраны судна
    # на соответствие требованиям КТМС-2006
    # расширение сферы деятельности
    # изменение содержания
    # квалификационные испытания сварщиков
    # технологические процессы сварки
    # рассмотрение II части Декларации о соответствии трудовым нормам в морском судоходстве   # noqa: E501
    # техническое наблюдение за ремонтом
    # квартальный отчёт
    # ----
    # OEX-продление/ Extension
    # OOS-вывод судна в отстой
    # (Recommission-вывод судна из отстоя)* для информации
    # ODM-Авария/ Damage
    # OAL-Переоборудовние/ Alteration
    # ORP-После ремонта/ AfterRepair
    # ORN-Реновация/ Renovation
    # ORF-Смена флага/ Reflagging
    # ORI-Восстановление класса после приостановки/ ReinstatementOfClass
    # ORA-Переназначение класса после снятия/ ReassignmentOfClass
    # TOC-Переклассификация/ TransferOfClass
    # PSC-Осв. судна, проверенного властями Госуддарства порта
    # FSI-Осв. судна, проверенного властями Государства флага
    # LA-Освидетельствование грузоподъёмных устройств
    # ILO-Освидетельствование на соответствие требованиям МОТ
    # ISM-Освидетельствование на соответствие требованиям МКУБ
    # ISPS-Освидетельствование на соответствие требованиям МК ОСПС
    # INT-Временное освидетельствование на соответствие требованиям МКУБ/МК ОСПС # noqa: E501
    # ADD-Дополнительное освидетельствование на соответствие требованиям МКУБ/МК ОСПС # noqa: E501
    # Reissued-Переоформление
    # Другое*

    class SurveyScope(models.TextChoices):
        """Выбор объёма освидетельствования."""

    # Объём освидетельствования (рус.)
    # внеочередное
    # возобновляющее
    # ежегодное
    # очередное
    # первоначальное
    # первичное
    # временное
    # подводной части судна
    # промежуточное
    # для выдачи временных документов
    # периодическое
    # дополнительное

    class SurveyObject(models.TextChoices):
        """Выбор объекта освидетельствования."""

    # Объекты освидетельствования
    # Судно
    # Судно по всем частям
    # Судно по корпусной части
    # Судно по механической части
    # Судно по электромеханической части
    # Судно по корпусной и механической частям
    # Судно по механической и электромеханической частям

    company = models.ForeignKey(
        Company,
        verbose_name="Компания",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    number = models.CharField(
        "Номер заявки", max_length=7, unique=True, blank=True
    )  # noqa: E501
    date = models.DateField("Дата заявки")
    completion_date = models.DateField(
        "Дата завершения заявки", null=True, blank=True
    )  # noqa: E501
    survey_code = models.CharField(
        "Код услуги",
        max_length=5,
        choices=SurveyCode.choices,
        blank=True,
        default="",
    )
    survey_type = models.CharField(
        "Вид освидетельствования",
        max_length=3,
        choices=SurveyType.choices,
        blank=True,
        default="",
    )
    survey_scope = models.CharField(
        "Объём освидетельствования",
        max_length=3,
        choices=SurveyScope.choices,
        blank=True,
        default="",
    )
    survey_object = models.CharField(
        "Объём освидетельствования",
        max_length=3,
        choices=SurveyObject.choices,
        blank=True,
        default="",
    )
    vessel = models.ForeignKey(
        Vessel,
        verbose_name="Судно",
        on_delete=models.SET_NULL,
        related_name="applications",
        null=True,
    )
    register_signer = models.ForeignKey(
        to=User,
        verbose_name="Подписывает от Регистра",
        on_delete=models.SET_DEFAULT,
        related_name="register_signer_applications",
        default=None,
        null=True,
    )
    applicant_signer = models.ForeignKey(
        to=Employee,
        verbose_name="Подписывает от Заказчика",
        on_delete=models.SET_NULL,
        related_name="applicant_signer_applications",
        null=True,
        blank=True,
    )
    authorized_person = models.ForeignKey(
        to=Employee,
        verbose_name="Уполномоченное лицо",
        on_delete=models.SET_NULL,
        related_name="authorized_person_applications",
        null=True,
        blank=True,
    )
    assigned_surveyors = models.ManyToManyField(
        to=User, verbose_name="Исполнители заявки"
    )  # noqa: E501
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время создания"
    )  # noqa: E501
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата и время обновления",
        null=True,
        blank=True,  # noqa: E501
    )  # noqa: E501
    created_by = models.ForeignKey(
        to=User,
        verbose_name="Создал",
        on_delete=models.SET_DEFAULT,
        related_name="creator_applications",
        default=None,
        null=True,
    )
    updated_by = models.ForeignKey(
        to=User,
        verbose_name="Обновил",
        on_delete=models.SET_NULL,
        related_name="updater_applications",
        null=True,
        blank=True,
    )

    objects = ApplicationManager()

    class Meta:
        """Сортировка."""

        ordering = [
            "number",
        ]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        """Возвращение строки."""
        return f"{self.number} РС{self.number}"
