# pylint: disable=too-few-public-methods, too-many-ancestors, line-too-long, import-error, no-member, invalid-name, too-many-branches  # noqa: E501
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

        C00001 = (
            "00001",
            "Классификационные освидетельствования судов в эксплуатации",
        )  # noqa: E501
        C00002 = "00002", "Техническое наблюдение за постройкой судна"
        C00003 = "00003", "Услуги по освидетельствованию судна в ремонте"
        C00004 = (
            "00004",
            "Техническое наблюдение за изготовлением материалов и изделий не судового назначения",  # noqa: E501
        )  # noqa: E501
        C00005 = "00005", "Техническое наблюдение за изготовлением стали"
        C00006 = "00006", "Рассмотрение технической документации"
        C00007 = "00007", "Обмер судов"
        C00008 = "00008", "Замещение ИКО"
        C00009 = "00009", "Техническое наблюдение за контейнерами"
        C00010 = "00010", "Прочие виды деятельности"
        C00011 = (
            "00011",
            "Освидетельствование на соответствие МКУБ, ОСПС, КТМС судов",
        )  # noqa: E501
        C00012 = (
            "00012",
            "Освидетельствование на соответствие другим МК судов в эксплуатации",  # noqa: E501
        )  # noqa: E501
        C00013 = "00013", "Добровольная сертификация"
        C00014 = (
            "00014",
            "Освидетельствование на соответствие МКУБ судовых компаний",
        )  # noqa: E501
        C00015 = (
            "00015",
            "Техническое наблюдение за изготовлением материалов и изделий для судов",  # noqa: E501
        )  # noqa: E501
        C00016 = (
            "00016",
            "Техническое наблюдение за постройкой МСП и трубопроводов",
        )  # noqa: E501
        C00100 = "00100", "Сертификация систем менеджмента качества"
        C00101 = (
            "00101",
            "Квалификационные испытания сварщиков и одобрение технологических процессов сварки (СОДС, СОТПС)",  # noqa: E501
        )  # noqa: E501
        C00102 = "00102", "Сертификация продукции в системе ГОСТ Р"
        C00103 = (
            "00103",
            "Освидетельствование предприятий, лабораторий на территории России (СП, ССП, СПИ, СПЛ)",  # noqa: E501
        )  # noqa: E501
        C00104 = (
            "00104",
            "Освидетельствование предприятий, лабораторий на территории других стран (не Россия)",  # noqa: E501
        )  # noqa: E501
        C00105 = (
            "00105",
            "Услуги по декларированию и сертификации навалочных и опасных грузов, сертификация тары",  # noqa: E501
        )  # noqa: E501
        C00120 = (
            "00120",
            "Техническое наблюдение согласно отчёту предприятия (с НДС)",
        )  # noqa: E501
        C00121 = (
            "00121",
            "Классификация и освидетельствование маломерного судна",
        )  # noqa: E501

    class SurveyType(models.TextChoices):
        """Выбор объёма освидетельствования."""

        ISM = "ISM", "На соответствие требованиям МКУБ"
        ISS = "ISS", "На соответствие требованиям МК ОСПС"
        MLC = "MLC", "На соответствие требованиям КТМС-2006"
        DII = (
            "DII",
            "Рассмотрение II части Декларации о соответствии трудовым нормам в морском судоходстве",  # noqa: E501
        )  # noqa: E501
        OCR = "OSC", "Офшорных контейнеров"
        TCR = "TCR", "Контейнеров-цистерн"
        EXP = "EXP", "Расширение сферы деятельности"
        CHA = "CHA", "Изменение содержания свидетельства"
        WAC = "WAC", "Квалификационные испытания сварщиков"
        WPS = "WPS", "Технологические процессы сварки"

    class SurveyScope(models.TextChoices):
        """Выбор вида освидетельствования."""

        INITIL = "I", "Первоначальное"  # noqa: E741
        ANNUAL = "A", "Ежегодное"
        INTERM = "IN", "Промежуточное"
        SPECIL = "S", "Очередное"
        RENEWL = "R", "Возобновляющее"
        BOTTOM = "D", "Подводной части судна"
        OCCASL = "O", "Внеочередное"  # noqa: E741
        CONTIN = "C", "Непрерывное"
        INTERI = "INT", "Временное (МКУБ, ОСПС, КТМС)"
        ADDITL = "ADD", "Дополнительное (МКУБ, ОСПС, КТМС)"  # noqa: E501
        PRIMAR = "PR", "Первичное (СОДС, СОТПС)"
        PERIOD = "PL", "Периодическое (СОДС, СОТПС)"

    class SurveyObject(models.TextChoices):
        """Выбор объекта освидетельствования."""

        SHIPPART = "SHIP", "Судно"
        ALLPARTS = "ALLP", "Судно по всем частям"
        HULLPART = "HULL", "Судно по корпусной части"
        MECHPART = "MECH", "Судно по механической части"
        ELECPART = "ELEC", "Судно по электромеханической части"
        HULLMECH = "HUME", "Судно по корпусной и механической частям"
        HULLELEC = (
            "HUEL",
            "Судно по корпусной и электромеханической частям",
        )  # noqa: E501
        MECHELEC = (
            "MEEL",
            "Судно по механической и электромеханической частям",
        )  # noqa: E501
        RADIPART = "RADI", "Судно по радиочасти"

    company = models.ForeignKey(
        Company,
        verbose_name="Компания",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    number = models.CharField("Номер заявки", max_length=15, unique=True)
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
        default=SurveyCode.C00001,
    )
    survey_type = models.CharField(
        "Код услуги детально (если применимо)",
        max_length=3,
        choices=SurveyType.choices,
        blank=True,
    )
    survey_scope = models.CharField(
        "Вид освидетельствования",
        max_length=3,
        choices=SurveyScope.choices,
        blank=True,
    )
    occasional_cause = models.TextField(
        "Уточнение сведений об услуге",
        max_length=127,
        blank=True,
    )
    occasional_cause_en = models.TextField(
        "Уточнение сведений об услуге на английском",
        max_length=127,
        blank=True,
    )
    survey_object = models.CharField(
        "Объекты освидетельствования",
        max_length=4,
        choices=SurveyObject.choices,
        blank=True,
        # default=SurveyObject.ALLPARTS,
    )
    vessel = models.ForeignKey(
        Vessel,
        verbose_name="Название судна",
        on_delete=models.PROTECT,
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

    def get_survey_type_en(self, survey_type_value):
        """Получить перевод вида освидетельствования
        на английский язык."""
        match survey_type_value:
            case self.SurveyType.CHA:
                result = "Changing content of the certificate"
            case self.SurveyType.DII:
                result = "Review of Declaration of Maritime Labour Compliance part II"  # noqa: E501
            case self.SurveyType.OCR:
                result = "The offshore containers"
            case self.SurveyType.TCR:
                result = "The tank-containers"
            case self.SurveyType.EXP:
                result = "Expanding field of activity"
            case self.SurveyType.ISM:
                result = "On compliance with the requirements of ISMC"
            case self.SurveyType.ISS:
                result = "On compliance with the requirements of ISPS IC"
            case self.SurveyType.MLC:
                result = "On compliance with the requirements of MLC-2006 Convention"  # noqa: E501
            case self.SurveyType.WAC:
                result = "Welder approvals"
            case self.SurveyType.WPS:
                result = "Welding procedure specifications"
            case _:
                return ""
        return result

    def get_survey_scope_en(self, survey_scope_value):
        """Получить перевод вида освидетельствования
        на английский язык."""
        match survey_scope_value:
            case self.SurveyScope.INITIL:
                result = "Initial"
            case self.SurveyScope.ANNUAL:
                result = "Annual"
            case self.SurveyScope.INTERM:
                result = "Intermediate"
            case self.SurveyScope.SPECIL:
                result = "Special"
            case self.SurveyScope.RENEWL:
                result = "Renewal"
            case self.SurveyScope.BOTTOM:
                result = "Bottom"
            case self.SurveyScope.OCCASL:
                result = "Occasional"
            case self.SurveyScope.CONTIN:
                result = "Continuous"
            case self.SurveyScope.INTERI:
                result = "Interim (ISM ISPS MLC)"
            case self.SurveyScope.ADDITL:
                result = "Additional (ISM ISPS MLC)"
            case self.SurveyScope.PRIMAR:
                result = "Primary (WAC WPSAC)"
            case self.SurveyScope.PERIOD:
                result = "Periodical (WAC WPSAC)"
            case _:
                return ""
        return result

    def __str__(self):
        """Человекочитаемое представление объекта."""
        SURVEY = "освидетельствование"
        SURVEY_EN = "survey"
        COMPANY = "компании"
        COMPANY_EN = "of the company"
        QUALIFICATION = "аттестация"
        QUALIFICATION_EN = "qualification"
        INTERIM_DOCS = (
            "для выдачи Временного Свидетельства"  # с целью выдачи врем. докум
        )
        INTERIM_DOCS_EN = "with the aim of issuing interim documents"
        CONT_RULES = "на соответствие требованиям Сборника правил РС по контейнерам/КБК"  # noqa: E501
        CONT_RULES_EN = "on compliance with the requirements of the RS Rule set on containers/CSC"  # noqa: E501
        SURVEY_CODES = self.SurveyCode
        SURVEY_TYPES = self.SurveyType
        SURVEY_SCOPES = self.SurveyScope
        survey_type_en = self.get_survey_type_en(self.survey_type)
        survey_scope_en = self.get_survey_scope_en(self.survey_scope)
        match self.survey_code:
            case SURVEY_CODES.C00001:
                if self.survey_scope not in [
                    SURVEY_SCOPES.OCCASL,
                    SURVEY_SCOPES.CONTIN,
                    SURVEY_SCOPES.BOTTOM,
                ]:  # noqa: E501
                    result = f"{self.get_survey_scope_display()} {SURVEY} / {survey_scope_en} {SURVEY_EN}"  # type: ignore # noqa: E501
                elif self.survey_scope == SURVEY_SCOPES.BOTTOM:
                    result = f"{SURVEY.capitalize()} {self.get_survey_scope_display().lower()} / {survey_scope_en} {SURVEY_EN}"  # type: ignore # noqa: E501
                else:
                    result = f"{self.get_survey_scope_display()} {SURVEY} {self.occasional_cause} / {survey_scope_en} {SURVEY_EN} {self.occasional_cause_en}"  # type: ignore # noqa: E501
            case SURVEY_CODES.C00002:
                if self.occasional_cause is not None:
                    result = f"Технаблюдение за постройкой: {self.occasional_cause} / Technical supervision for shipbuilding: {self.occasional_cause_en}"  # noqa: E501
                else:
                    result = f"{self.get_survey_code_display()} / Technical supervision for shipbuilding"  # type: ignore # noqa: E501
            case SURVEY_CODES.C00003:
                result = f"{self.get_survey_code_display()} / Services on survey of a ship in repair"  # type: ignore # noqa: E501
            case SURVEY_CODES.C00006:
                result = f'{self.get_survey_code_display()} "{self.occasional_cause}" на т/х {self.vessel} / Review of technical documentation "{self.occasional_cause_en}" on m/v {self.vessel.name_en}'  # type: ignore # noqa: E501
            case SURVEY_CODES.C00009:
                try:
                    result = f"{self.get_survey_scope_display().split()[0]} {SURVEY} {self.get_survey_type_display()[0].lower()}{self.get_survey_type_display()[1:]} {CONT_RULES} - {self.occasional_cause} шт. / {survey_scope_en.split()[0]} {SURVEY_EN} {survey_type_en[0].lower()}{survey_type_en[1:]} {CONT_RULES_EN} - {self.occasional_cause} pcs"  # type: ignore # noqa: E501
                except IndexError:
                    result = f"{self.get_survey_scope_display().split()[0]} {SURVEY} (выберите вид освидетельствования) / {survey_scope_en.split()[0]} {SURVEY_EN} (choose type of survey)"  # type: ignore # noqa: E501
            case SURVEY_CODES.C00011:
                # SURVEY_SCOPES.PRIMAR excluded
                if self.survey_scope not in [
                    SURVEY_SCOPES.ADDITL,
                    SURVEY_SCOPES.INTERI,
                ]:  # noqa: E501
                    if self.survey_type != SURVEY_TYPES.DII:  # noqa: E501
                        try:
                            result = f"{self.get_survey_scope_display()} {SURVEY} {self.get_survey_type_display()[0].lower()}{self.get_survey_type_display()[1:]} / {survey_scope_en} {SURVEY_EN} {survey_type_en[0].lower()}{survey_type_en[1:]}"  # type: ignore # noqa: E501
                        except IndexError:
                            result = f"{self.get_survey_scope_display()} {SURVEY} (выберите вид освидетельствования) / {survey_scope_en} {SURVEY_EN} (choose type of survey)"  # type: ignore # noqa: E501
                    else:
                        result = f"{self.get_survey_type_display()} / {survey_type_en}"  # type: ignore # noqa: E501
                elif self.survey_scope == SURVEY_SCOPES.ADDITL:
                    try:
                        result = f"{self.get_survey_scope_display().split()[0]} {SURVEY} {self.get_survey_type_display()[0].lower()}{self.get_survey_type_display()[1:]} / {survey_scope_en.split()[0]} {SURVEY_EN} {survey_type_en[0].lower()}{survey_type_en[1:]}"  # type: ignore # noqa: E501
                    except IndexError:
                        result = f"{self.get_survey_scope_display().split()[0]} {SURVEY} (выберите вид освидетельствования) / {survey_scope_en.split()[0]} {SURVEY_EN} (choose type of survey)"  # type: ignore # noqa: E501
                else:
                    try:
                        result = f"{SURVEY.capitalize()} {self.get_survey_type_display()[0].lower()}{self.get_survey_type_display()[1:]} {INTERIM_DOCS} / {SURVEY_EN.capitalize()} {survey_type_en[0].lower()}{survey_type_en[1:]} {INTERIM_DOCS_EN}"  # type: ignore # noqa: E501
                    except IndexError:
                        result = f"{SURVEY.capitalize()} (выберите вид освидетельствования) / {SURVEY_EN.capitalize()} (choose type of survey)"  # type: ignore # noqa: E501
            case SURVEY_CODES.C00014:
                if self.survey_scope not in [
                    SURVEY_SCOPES.ADDITL,
                    SURVEY_SCOPES.INTERI,
                ]:  # noqa: E501
                    result = f"{self.get_survey_scope_display()} {SURVEY} {COMPANY} на соответствие требованиям МКУБ / {survey_scope_en} {SURVEY_EN} {COMPANY_EN} on compliance with the requirements of the ISMC"  # type: ignore # noqa: E501
                elif self.survey_scope == SURVEY_SCOPES.ADDITL:
                    result = f"{self.get_survey_scope_display().split()[0]} {SURVEY} {COMPANY} по МКУБ / {survey_scope_en.split()[0]} {SURVEY_EN} {COMPANY_EN} on ISMC"  # type: ignore # noqa: E501
                else:
                    result = f"{SURVEY.capitalize()} {COMPANY} по МКУБ {INTERIM_DOCS} / {SURVEY_EN.capitalize()} {COMPANY_EN} on ISMC {INTERIM_DOCS_EN}"  # type: ignore # noqa: E501
            case SURVEY_CODES.C00015:
                result = (
                    f"{SURVEY.capitalize()} / {SURVEY_EN.capitalize()} of"  # noqa: E501
                )
            case SURVEY_CODES.C00101:
                if self.survey_type == SURVEY_TYPES.WAC:
                    if self.survey_scope == SURVEY_SCOPES.PRIMAR:
                        result = f"Первичная {QUALIFICATION} сварщиков - {self.occasional_cause} чел. / Primary {QUALIFICATION_EN} of welders - {self.occasional_cause} prs"  # noqa: E501
                    else:
                        result = f"Периодическая {QUALIFICATION} сварщиков без проведения практических испытаний - {self.occasional_cause} чел. / Periodical {QUALIFICATION_EN} of welders without conducting practical tests - {self.occasional_cause} prs"  # noqa: E501
                else:
                    if self.survey_scope == SURVEY_SCOPES.PRIMAR:
                        result = f"Одобрение технологического процесса сварки - {self.occasional_cause} шт. / Approval of the welding procedure specification - {self.occasional_cause} pcs"  # noqa: E501
                    else:
                        result = f"Подтверждение Свидетельства об одобрении технологического процесса сварки (без испытаний) - {self.occasional_cause} шт. / Endorsing Welding procedure approval test certificate (without tests) - {self.occasional_cause} pcs"  # noqa: E501
            case SURVEY_CODES.C00103 | SURVEY_CODES.C00104:
                if self.survey_type not in [
                    SURVEY_TYPES.EXP,
                    SURVEY_TYPES.CHA,
                ]:  # noqa: E501
                    result = f"{self.get_survey_scope_display()} {SURVEY} {self.occasional_cause} / {survey_scope_en} {SURVEY_EN} {self.occasional_cause}"  # type: ignore # noqa: E501
                else:
                    try:
                        result = f"{self.get_survey_scope_display()} {SURVEY} в связи с {self.get_survey_type_display().split()[0].lower()}м {self.get_survey_type_display().split()[1]} {self.get_survey_type_display().split()[2]} {self.occasional_cause} / {survey_scope_en} {SURVEY_EN} in connection with {survey_type_en.split()[0].lower()} {survey_type_en.split()[1:]} {self.occasional_cause}"  # type: ignore # noqa: E501
                    except IndexError:
                        result = f"{self.get_survey_scope_display()} {SURVEY} в связи с (выберите вид освидетельствования) {self.occasional_cause} / {survey_scope_en} {SURVEY_EN} in connection with (choose type of survey) {self.occasional_cause}"  # type: ignore # noqa: E501
            case SURVEY_CODES.C00121:
                if self.survey_scope != SURVEY_SCOPES.OCCASL:
                    result = f"{self.get_survey_scope_display()} {SURVEY} маломерного судна"  # type: ignore # noqa: E501
                else:
                    result = f"{self.get_survey_scope_display()} {SURVEY} маломерного судна {self.occasional_cause}"  # type: ignore # noqa: E501
            case _:
                result = f"Функционал '{self.get_survey_code_display()}' в разработке"  # type: ignore # noqa: E501
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

        INBUILDING = "01", "01 - Судно в постройке на класс РС"
        INSERVCLAS = (
            "02",
            "02 - Судно в эксплуатации в стадии присвоения класса РС",
        )  # noqa: E501
        INSIACSTAD = (
            "03",
            "03- Судно в эксплуатации с классом ИКО в стадии выдачи РС конвенционных документов",  # noqa: E501
        )  # noqa: E501
        INSRCOSTAD = (
            "04",
            "04 - Судно в эксплуатации с классом РКО и флагом РФ в стадии выдачи РС конвенционных документов",  # noqa: E501
        )  # noqa: E501
        SUPVISUSPD = (
            "06",
            "06 - Техническое наблюдение за постройкой судна приостановлено",
        )  # noqa: E501
        APPLICWDRN = "07", "07 - Заявка аннулирована"
        BUIDCEASED = "08", "08 - Строительство прекращено"
        BUILDSUSPD = (
            "09",
            "09 - Постройка законсервирована, освидетельствование не выполняется",  # noqa: E501
        )  # noqa: E501
        BUILDINTED = (
            "10",
            "10 - Судно предполагается к строительству на класс РС",
        )  # noqa: E501
        INSERVICE = "11", "11 - Класс действует (в эксплуатации)"
        INREPAIR = "12", "12 - В ремонте"
        LAIDUP = "13", "13 - Класс действует (в отстое)"
        RESERVED = "14", "14 - Резервный код"
        INSFORSEMR = "15", "15 - Класс действует (форс-мажор)"
        INSURVEY = (
            "16",
            "16 - Класс действует (судно в процессе освидетельствования)",
        )
        SUSPDAMAGE = "21", "21 - Класс приостановлен (аварийный случай)"
        SUSPOVRDUE = (
            "22",
            "22 - Класс приостановлен (просрочено освидетельствование)",
        )
        SUSPENVELP = "23", "23 - Класс приостановлен (судно в консервации)"
        SUSPLUPOVD = (
            "24",
            "24 - Класс приостановлен в отстое (просрочено освидетельствование)",  # noqa: E501
        )
        SUSPLAIDUP = (
            "25",
            "25 - Класс приостановлен (судно выведено в отстой с приостановленным классом)",  # noqa: E501
        )
        SUSPREQOVD = (
            "26",
            "26 - Класс приостановлен (невыполнение требований или условий сохранения класса)",  # noqa: E501
        )
        SUSPOTHERS = (
            "27",
            "27 - Класс приостановлен (причины, не связаные с безопасностью)",
        )
        SUSPINSURV = (
            "28",
            "28 - Класс приостановлен (судно в процессе освидетельствования для восстановления класса)",  # noqa: E501
        )
        WDRANOWNER = "31", "31 - Класс снят (просьба судовладельца)"
        WDRANPASSD = (
            "32",
            "32 - Класс снят (истекли 6 месяцев после приостановки класса)",
        )
        WDRANRULES = (
            "33",
            "33 - Класс снят (невыполнение требований Правил РС)",
        )  # noqa: E501
        WDRANOTHER = (
            "34",
            "34 - Класс снят (причины, не связаные с безопасностью)",
        )  # noqa: E501
        WDRANSCAPD = (
            "41",
            "41 - Класс снят (разделано или продано для разделки на металлолом)",  # noqa: E501
        )
        WDRANWRECK = "42", "42 - Класс снят (гибель)"
        WDRANDAMAG = "43", "43 - Класс снят (аварийный случай)"
        INSREINSTD = (
            "51",
            "51 - Класс действует (восстановлен после приостановки)",
        )  # noqa: E501
        INSREASSIG = "52", "52 - Класс действует (переназначен после снятия)"
        INSTRANSIA = (
            "61",
            "61 - Класс действует (принято в класс РС из класса общества-члена МАКО)",  # noqa: E501
        )
        INSTRNONIA = (
            "62",
            "62 - Класс действует (принято в класс РС из класса общества-не члена МАКО)",  # noqa: E501
        )
        WDRANTOIAC = (
            "71",
            "71 - Класс снят (переход из класса РС в класс общества-члена МАКО)",  # noqa: E501
        )
        WDRANTONIA = (
            "72",
            "72 - Класс снят (переход из класса РС в класс общества-не члена МАКО)",  # noqa: E501
        )
        SMCRINSERV = "80", "80 - Маломерное прогулочное судно в эксплуатации"
        SMCRNOTINS = (
            "90",
            "90 - Маломерное прогулочное судно не в эксплуатации",
        )  # noqa: E501
        IACSCLASS = "99", "99 - Класс ИКО"

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
