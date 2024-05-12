# pylint: disable=too-few-public-methods, too-many-ancestors, line-too-long, import-error, no-member, invalid-name, too-many-branches # noqa: E501
"""ОРМ модели application."""

from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.services.mixins import CreatorMixin, UpdaterMixin
from modules.companies.models import Company, Employee, PlaceMixin

from .vessel import Vessel


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


class Application(PlaceMixin, CreatorMixin, UpdaterMixin):
    """Модель заявок."""

    class ApplicationManager(models.Manager):
        """Менеджер модели заявок."""

        def all(self):
            """Оптимизация запросов модели заявок."""
            return (
                self.get_queryset()
                # .prefetch_related("assigned_surveyors")
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

        SHIPSURVEY = (
            "00001",
            "Классификационные освидетельствования судов в эксплуатации",
        )  # noqa: E501
        SHIPBUILDING = "00002", "Техническое наблюдение за постройкой судна"
        SHIPREPAIR = "00003", "Услуги по освидетельствованию судна в ремонте"
        NONSHIPPROD = (
            "00004",
            "Техническое наблюдение за изготовлением материалов и изделий не судового назначения",  # noqa: E501
        )
        STEELPROD = "00005", "Техническое наблюдение за изготовлением стали"
        TECHDOCUM = "00006", "Рассмотрение технической документации"
        TONNAGE = "00007", "Обмер судов"
        BEHALFIACS = "00008", "Замещение ИКО"
        CONTAINER = "00009", "Техническое наблюдение за контейнерами"
        OTHERACTIV = "00010", "Прочие виды деятельности"
        ISMISPSILO = (
            "00011",
            "Освидетельствование на соответствие МКУБ, ОСПС, КТМС судов",
        )
        OTHERCONV = (
            "00012",
            "Освидетельствование на сответствие другим МК судов в эксплуатации",  # noqa: E501
        )
        VOLUNTARY = "00013", "Добровольная сертификация"
        ISMCOMPANY = (
            "00014",
            "Освидетельствование на соответствие МКУБ судовых компаний",
        )
        SHIPPRODUCT = (
            "00015",
            "Техническое наблюдение за изготовлением материалов и изделий для судов",  # noqa: E501
        )
        PIPELINE = (
            "00016",
            "Техническое наблюдение за постройкой МСП и трубопроводов",
        )
        QMANAGESYS = "00100", "Сертификация систем менеджмента качества"
        WELDING = (
            "00101",
            "Квалификационные испытания сварщиков и одобрение технологических процессов сварки (СОДС, СОТПС)",  # noqa: E501
        )
        GOSTRPROD = "00102", "Сертификация продукции в системе ГОСТ Р"
        COMPANYRUREG = (
            "00103",
            "Освидетельствование предприятий, лабораторий на территории России (СП, ССП, СПИ, СПЛ)",  # noqa: E501
        )
        COMPANYNOTRU = (
            "00104",
            "Освидетельствование предприятий, лабораторий на территории других стран (не Россия)",  # noqa: E501
        )
        DANGEROUSG = (
            "00105",
            "Услуги по декларированию и сертификации навалочных и опасных грузов, сертификация тары",  # noqa: E501
        )
        ONREPORTVAT = (
            "00120",
            "Техническое наблюдение согласно отчёту предприятия (с НДС)",
        )
        SMALLCRAFTS = (
            "00121",
            "Классификация и освидетельствование маломерного судна",
        )

    class SurveyType(models.TextChoices):
        """Выбор вида освидетельствования."""

        ISM = "ISM", "На соответствие требованиям МКУБ"
        ISPS = "ISS", "На соответствие требованиям МК ОСПС"
        MLC2006 = "MLC", "На соответствие требованиям КТМС-2006"
        MLCDPII = (
            "DII",
            "Рассмотрение II части Декларации о соответствии трудовым нормам в морском судоходстве",  # noqa: E501
        )
        EXPAND = "EXP", "Расширение сферы деятельности"
        CHANGE = "CHA", "Изменение содержания свидетельства"
        WELDER = "WAC", "Квалификационные испытания сварщиков"
        WELDPS = "WPS", "Технологические процессы сварки"

    class SurveyScope(models.TextChoices):
        """Выбор объёма освидетельствования."""

        INITIAL = "I", "Первоначальное"
        ANNUAL = "A", "Ежегодное"
        INTERMEDIATE = "IN", "Промежуточное"
        SPECIAL = "S", "Очередное"
        RENEWAL = "R", "Возобновляющее"
        BOTTOM = "D", "Подводной части судна"
        OCCASIONAL = "O", "Внеочередное"
        CONTINUOUS = "C", "Непрерывное"
        INTERIM = "INT", "Временное (МКУБ, ОСПС, КТМС)"
        ADDITIONAL = "ADD", "Дополнительное (МКУБ, ОСПС, КТМС)"
        PRIMARY = "PR", "Первичное (СОДС, СОТПС)"
        PERIODICAL = "PL", "Периодическое (СОДС, СОТПС)"

    class SurveyObject(models.TextChoices):
        """Выбор объекта освидетельствования."""

        SHIP = "SHIP", "Судно"
        ALL = "ALL", "Судно по всем частям"
        HULL = "HULL", "Судно по корпусной части"
        MECH = "MECH", "Судно по механической части"
        ELEC = "ELEC", "Судно по электромеханической части"
        HUME = "HUME", "Судно по корпусной и механической частям"
        MEEL = "MEEL", "Судно по механической и электромеханической частям"

    company = models.ForeignKey(
        Company,
        verbose_name="Компания",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    number = models.CharField("Номер заявки", max_length=7, unique=True)
    date = models.DateField("Дата заявки")
    completion_date = models.DateField(
        "Дата завершения заявки",
        null=True,
        blank=True,
    )
    survey_code = models.CharField(
        "Код услуги",
        max_length=5,
        choices=SurveyCode.choices,
        default="00001",
    )
    survey_type = models.CharField(
        "Вид освидетельствования",
        max_length=3,
        choices=SurveyType.choices,
        blank=True,
        default="00001",
    )
    survey_scope = models.CharField(
        "Объём освидетельствования",
        max_length=3,
        choices=SurveyScope.choices,
        blank=True,
    )
    occasional_cause = models.TextField(
        "Уточнение сведений об услуге",  # noqa: E501
        max_length=127,
        blank=True,  # noqa: E501
    )
    survey_object = models.CharField(
        "Объекты освидетельствования",
        max_length=4,
        choices=SurveyObject.choices,
        blank=True,
        default="ALLO",
    )
    vessel = models.ForeignKey(
        Vessel,
        verbose_name="Название судна",
        on_delete=models.SET_NULL,
        related_name="applications",
        null=True,
        blank=True,
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

    objects = ApplicationManager()

    class Meta:
        """Сортировка."""

        ordering = [
            "-number",
        ]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        """Возвращение строки."""
        SURVEY = "освидетельствование"
        QUALIFICATION = "аттестация"
        survey_code_string = self.get_survey_code_display()  # type: ignore
        survey_type_string = self.get_survey_type_display()  # type: ignore
        survey_scope_string = self.get_survey_scope_display()  # type: ignore
        match self.survey_code:
            case "00001":
                if self.survey_scope not in ["O", "C", "D"]:
                    result = f"{survey_scope_string} {SURVEY}"  # type: ignore # noqa: E501
                elif self.survey_scope == "D":
                    result = f"{SURVEY.capitalize()} {survey_scope_string.lower()}"  # type: ignore # noqa: E501
                else:
                    result = f"{survey_scope_string} {SURVEY} {self.occasional_cause}"  # type: ignore # noqa: E501
            case "00002":
                if self.occasional_cause is not None:
                    result = f"Технаблюдение за постройкой: {self.occasional_cause}"  # noqa: E501
                else:
                    result = survey_code_string
            case "00003":
                result = survey_code_string
            case "00006":
                result = f"{survey_code_string} {self.occasional_cause} на т/х {self.vessel}"  # type: ignore # noqa: E501
            case "00011":
                if self.survey_scope not in ["ADD", "INT"]:
                    result = f"{survey_scope_string} {SURVEY} {survey_type_string[0].lower()}{survey_type_string[1:]}"  # noqa: E501
                else:
                    result = f"{survey_scope_string.split()[0]} {SURVEY} {survey_type_string[0].lower()}{survey_type_string[1:]}"  # noqa: E501
            case "00015":
                result = f"{SURVEY.capitalize()} объектов технаблюдения:"  # type: ignore # noqa: E501
            case "00101":
                if self.survey_type == "WAC":
                    if self.survey_scope == "PR":
                        result = f"Первичная {QUALIFICATION} сваршиков - {self.occasional_cause} чел."  # noqa: E501
                    else:
                        result = f"Периодическая {QUALIFICATION} сварщиков без проведения практических испытаний - {self.occasional_cause} чел."  # noqa: E501
                else:
                    if self.survey_scope == "PR":
                        result = f"Одобрение технологического процесса сварки - {self.occasional_cause} шт."  # noqa: E501
                    else:
                        result = f"Подтверждение Свидетельства об одобрении технологического процесса сварки (без испытаний) - {self.occasional_cause} шт."  # noqa: E501
            case "00103":
                if self.survey_type not in ["EXP", "CHA"]:
                    result = f"{survey_scope_string} {SURVEY} {self.occasional_cause}"  # noqa: E501
                else:
                    result = f"{survey_scope_string} {SURVEY} в связи с {survey_type_string.split()[0].lower()}м {survey_type_string.split()[1]} {survey_type_string.split()[2]} {self.occasional_cause}"  # noqa: E501
            case "00121":
                if self.survey_scope != "O":
                    result = f"{survey_scope_string} {SURVEY} маломерного судна"  # type: ignore # noqa: E501
                else:
                    result = f"{survey_scope_string} {SURVEY} маломерного судна {self.occasional_cause}"  # type: ignore # noqa: E501
            case _:
                result = f"Функционал с кодом'{self.survey_code}' в разработке"
        return result

    def get_absolute_url(self):
        """Полный URL заявки фирмы."""
        return reverse("application_detail", kwargs={"slug": self.company.slug, "pk": self.id})  # type: ignore # noqa: E501


class VesselExtraInfo(PlaceMixin):
    """Модель доп. сведений по судну для договоров-заявок и отчётов."""

    class VesselExtraInfoManager(models.Manager):
        """Менеджер модели vessel_extra_info."""

        def all(self):
            """Оптимизация запросов модели vessel_extra_info."""
            return (
                self.get_queryset()
                .select_related("city")
                .select_related("application")
                .prefetch_related("assigned_surveyors")
            )

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

    class_status = models.CharField(
        "Текущий статус состояния класса судна",
        choices=ClassStatus.choices,
        max_length=2,
        blank=True,
    )
    due_date = models.DateField(
        verbose_name="Дата ближайщего предписанного освид. или выполнения треб.",  # noqa: E501
        null=True,
        blank=True,
    )
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="Номер заявки",
    )
    previous_survey_date = models.DateField(
        verbose_name="Дата предыдущего освидетельствования",
        null=True,
        blank=True,
    )
    last_psc_inspection_date = models.DateField(
        verbose_name="Дата последней проверки судна властями государства порта",  # noqa: E501
        null=True,
        blank=True,
    )
    last_psc_inspection_result = models.TextField(
        "Результаты последней проверки судна властями государства порта",
        blank=True,
    )
    completion_expected_date = models.DateField(
        verbose_name="Ориентировочная дата завершения ремонта",
        null=True,
        blank=True,
    )
    assigned_surveyors = models.ManyToManyField(
        to=User, verbose_name="Исполнители заявки"
    )

    objects = VesselExtraInfoManager()

    class Meta:
        """ЧЧИ."""

        verbose_name = "Дополнительные сведения по судну и заявке"
        verbose_name_plural = "Дополнительные сведения по судам и заявкам"

    def __str__(self):
        """Возвращение строки."""
        return f"Заявка № {self.application.number} от {self.application.date.strftime("%d.%m.%Y")}"  # type: ignore # noqa: E501

    def get_absolute_url(self):
        """Полный URL доп. данных по судну и заявке."""
        return reverse("vesselextrainfo_detail", kwargs={"slug": self.application.company.slug, "pk": self.application.id})  # type: ignore # noqa: E501
