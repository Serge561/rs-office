# pylint: disable=line-too-long, unused-variable, redefined-builtin, invalid-name, too-many-arguments, too-many-branches, too-many-locals, too-many-statements, too-many-return-statements,  # noqa: E501
"""Представления для модели applications-печать."""

import io
import datetime
import string
from decimal import Decimal
import pymorphy3
from transliterate import translit, detect_language
from petrovich.main import Petrovich
from petrovich.enums import Case
from num2words import num2words
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import dateformat
from docxtpl import DocxTemplate
from ..models import Application, BankAccount, Company, Employee, Form

User = get_user_model()

RS_RU_BRANCHES = (
    "110",
    "112",
    "114",
    "120",
    "121",
    "125",
    "130",
    "131",
    "141",
    "150",
    "170",
    "171",
    "172",
    "173",
    "174",
    "184",
    "190",
)

AGREEMENT_APPLICATION = "agreement"
ACCEPTANCE = "acceptance"
RS_BRANCH_NAME_FIRST_CHARS = "РС,"
GONORATIVE = "Mr/Mrs"

TEMPLATES = {
    "LISTREGI": "List_registratsii_proverki_dokumentov.docx",
    "PAGE404R": "404_page.docx",
    "T43031": "430_3_1.docx",
    "T43033": "430_3_3.docx",
    "T43034": "430_3_4.docx",
    "T43034B": "430_3_4_b.docx",
    "T43035": "430_3_5.docx",
    "T43035B": "430_3_5_b.docx",
    "T81011": "810_1_1.docx",
    "T81011E": "810_1_1_en.docx",
    "T81012P": "810_1_2_p.docx",
    "T81012PE": "810_1_2_p_en.docx",
    "T81012S": "810_1_2_s.docx",
    "T81012SE": "810_1_2_s_en.docx",
    "T81012W": "810_1_2_w.docx",
    "T81012WE": "810_1_2_w_en.docx",
    "T8101101": "810_1_10_1.docx",
    "T810110": "810_1_10.docx",
    "T810111E": "810_1_11_en.docx",
    "T810111": "810_1_11.docx",
}


def get_docx_template(
    survey_code, report_type, rs_branch, survey_scope=None
):  # noqa: E501
    """Получить определённый шаблон docx в зависимости
    от кода услуги и подразделения. Notes:
     - report_type is certificate on AGREEMENT-application or,
     - ACCEPTANCE of delivery service report,
     - SHEET is document check sheet."""
    if rs_branch not in RS_RU_BRANCHES:
        match survey_code:
            case (
                Application.SurveyCode.C00001
                | Application.SurveyCode.C00003
                | Application.SurveyCode.C00011
            ):  # noqa: E501
                if report_type == AGREEMENT_APPLICATION:
                    template = TEMPLATES["T81011E"]
                elif report_type == ACCEPTANCE:
                    template = TEMPLATES["T43035"]
                else:
                    template = TEMPLATES["LISTREGI"]
            case Application.SurveyCode.C00002:
                if report_type == AGREEMENT_APPLICATION:
                    template = TEMPLATES["T81011E"]
                elif report_type == ACCEPTANCE:
                    template = TEMPLATES["T43035B"]
                else:
                    template = TEMPLATES["LISTREGI"]
            case Application.SurveyCode.C00006:
                if report_type == AGREEMENT_APPLICATION:
                    template = TEMPLATES["T810111E"]
                else:
                    template = TEMPLATES["T43035"]
            case Application.SurveyCode.C00015:
                if report_type == AGREEMENT_APPLICATION:
                    template = TEMPLATES["T81012PE"]
                else:
                    template = TEMPLATES["T43035"]
            case Application.SurveyCode.C00101 | Application.SurveyCode.C00009:
                if report_type == AGREEMENT_APPLICATION:
                    template = TEMPLATES["T81012WE"]
                else:
                    template = TEMPLATES["T43035"]
            case Application.SurveyCode.C00104 | Application.SurveyCode.C00014:
                if report_type == AGREEMENT_APPLICATION:
                    template = TEMPLATES["T81012SE"]
                else:
                    template = TEMPLATES["T43035"]
            case _:
                # создать логику вывода сообщения на
                # экран или все шаблоны сделать
                template = TEMPLATES["PAGE404R"]
        return template
    match survey_code:
        case (
            Application.SurveyCode.C00001
            | Application.SurveyCode.C00003
            | Application.SurveyCode.C00011
        ):  # noqa: E501
            if report_type == AGREEMENT_APPLICATION:
                template = TEMPLATES["T81011"]
            elif report_type == ACCEPTANCE:
                template = TEMPLATES["T43034"]
            else:
                template = TEMPLATES["LISTREGI"]
        case Application.SurveyCode.C00002:
            if report_type == AGREEMENT_APPLICATION:
                template = TEMPLATES["T81011"]
            elif report_type == ACCEPTANCE:
                template = TEMPLATES["T43034B"]
            else:
                template = TEMPLATES["LISTREGI"]
        case Application.SurveyCode.C00006:
            if report_type == AGREEMENT_APPLICATION:
                template = TEMPLATES["T810111"]
            else:
                template = TEMPLATES["T43031"]
        case Application.SurveyCode.C00015:
            if report_type == AGREEMENT_APPLICATION:
                template = TEMPLATES["T81012P"]
            else:
                template = TEMPLATES["T43033"]
        case (
            Application.SurveyCode.C00101 | Application.SurveyCode.C00009
        ):  # noqa: E501
            if report_type == AGREEMENT_APPLICATION:
                template = TEMPLATES["T81012W"]
            else:
                template = TEMPLATES["T43031"]
        case (
            Application.SurveyCode.C00103 | Application.SurveyCode.C00014
        ):  # noqa: E501
            if report_type == AGREEMENT_APPLICATION:
                template = TEMPLATES["T81012S"]
            else:
                template = TEMPLATES["T43031"]
        case Application.SurveyCode.C00121:
            if report_type == AGREEMENT_APPLICATION:
                if survey_scope == Application.SurveyScope.INITIL:
                    template = TEMPLATES["T810110"]
                else:
                    template = TEMPLATES["T8101101"]
            elif report_type == ACCEPTANCE:
                template = TEMPLATES["T43034"]
            else:
                template = TEMPLATES["LISTREGI"]
        case _:
            # создать логику вывода сообщения на
            # экран или все шаблоны сделать
            template = TEMPLATES["PAGE404R"]
    return template


def get_genitive_case_lastname(lastname):
    """Функция перевода фамилий в родительный падеж."""
    # to fix the bug with a last name see link below:
    # https://github.com/damirazo/Petrovich/issues/8
    p = Petrovich()
    cased_lname = p.lastname(lastname, Case.GENITIVE)
    return cased_lname


def get_genitive_case(phrase):
    """Функция перевода слов в родительный падеж."""
    # parse a phrase with punctuation, conj and prepos
    common_list = []
    morph = pymorphy3.MorphAnalyzer()
    words = phrase.split()
    not_caseable_char_list = [
        word
        for word in words
        if len(word) <= 5
        or word[-1] in string.punctuation
        or detect_language(word) != "ru"
        or word.isdigit()
    ]
    for word in words:
        if word not in not_caseable_char_list:
            common_list.append(morph.parse(word)[0].inflect({"gent"}).word)  # type: ignore # noqa: E501
        else:
            if word != "Устав":
                common_list.append(word)
            else:
                common_list.append("Устава")
    phrase_cased = " ".join(common_list)
    return phrase_cased


def get_signer_cased(
    position,
    lastname,
    firstname,
    middlename=None,
    rs_branch=None,
    position_en=None,
    is_register=False,
    firstname_en=None,
    lastname_en=None,
):  # noqa: E501
    """Получить имя и должность заявителя или представителя РС в
    родительном падеже и их перевод на английский язык (транслитерацию)
    для двуязычных форм в зависимости от расположения филиала."""
    if rs_branch in RS_RU_BRANCHES:
        if middlename is None:
            return f"{get_genitive_case(str(position))} {get_genitive_case_lastname(lastname)} {firstname[0]}."  # type: ignore # noqa: E501
        return f"{get_genitive_case(str(position))} {get_genitive_case_lastname(lastname)} {firstname[0]}. {middlename[0]}."  # type: ignore # noqa: E501
    if is_register is False:
        if detect_language(lastname) != "ru":
            if middlename is None:
                return f"{position}/{position_en} {GONORATIVE} {firstname[0]}. {lastname}"  # noqa: E501
            return f"{position}/{position_en} {GONORATIVE} {firstname[0]}. {middlename[0]}. {lastname}"  # noqa: E501
        if middlename is None:
            return f"{get_genitive_case(str(position))} {get_genitive_case_lastname(lastname)} {firstname[0]}. / {position_en} {translit(firstname[0], 'ru', reversed=True)}. {translit(lastname, 'ru', reversed=True)}"  # noqa: E501
        return f"{get_genitive_case(str(position))} {get_genitive_case_lastname(lastname)} {firstname[0]}. {middlename[0]}. / {position_en} {translit(firstname[0], 'ru', reversed=True)}. {translit(middlename[0], 'ru', reversed=True)}. {translit(lastname, 'ru', reversed=True)}"  # noqa: E501
    return f"{get_genitive_case(str(position))} {get_genitive_case_lastname(lastname)} {firstname[0]}. {middlename[0]}. / {position_en} {firstname_en[0]}. {lastname_en}"  # type: ignore # noqa: E501


def get_proxy_en(proxy_value):
    """Получить перевод документа-основания
    на английский язык для двуязычных форм."""
    match proxy_value:
        case Employee.ProxyType.ORDER:
            result = "Order"
        case Employee.ProxyType.CHARTER:
            result = "Charter"
        case Employee.ProxyType.PROXY:
            result = "Power of attorney"
        case Employee.ProxyType.REGISTERCERT:
            result = "Certificate of registry"
        case Employee.ProxyType.MMCRF:
            result = "Merchant shipping code (MSC RF)"
        case _:
            return ""
    return result


def get_genitive_case_proxy(
    proxy, proxy_label, number=None, date=None, rs_branch=None
):  # noqa: E501
    """Функция перевода названий документов,
    на основании которых действует заявитель,
    в родительный падеж."""
    proxy_label_cased = get_genitive_case(proxy_label)
    proxy_label_cased_capitalized = (
        proxy_label_cased[0].upper() + proxy_label_cased[1:]
    )  # noqa: E501
    match proxy:
        case (
            Employee.ProxyType.CHARTER
            | Employee.ProxyType.MMCRF
            | Employee.ProxyType.ORDER
            | Employee.ProxyType.REGISTERCERT
        ):
            power_of_attoney_gen = (
                f"{proxy_label_cased_capitalized} / {get_proxy_en(proxy)}"  # noqa: E501
            )
        case Employee.ProxyType.PROXY:
            power_of_attoney_gen = f"{proxy_label_cased_capitalized} № {number} от {is_none(date)} / {get_proxy_en(proxy)} No. {number} dd {is_none(date)}"  # type: ignore # noqa: E501
        case _:
            power_of_attoney_gen = proxy_label
    if rs_branch not in RS_RU_BRANCHES:
        return power_of_attoney_gen
    return power_of_attoney_gen.split(" / ", maxsplit=1)[0]


def is_none(value):
    """Проверка значений на None."""
    if value is None or value == "":
        return "--"
    if isinstance(value, datetime.date):
        return value.strftime("%d.%m.%Y")
    return value


def is_vessel_none(vessel=None, argument=None, rs_branch=None):
    """Проверка судна на None для заявок в промышленности."""
    vessel_attribute = ""
    if vessel is not None:
        match argument:
            case "name":
                if vessel.flag != "RU" or rs_branch in RS_RU_BRANCHES:
                    vessel_attribute = f'"{vessel.name}"'
                else:
                    vessel_attribute = f'"{vessel.name}" / "{vessel.name_en}"'
            case "rs":
                vessel_attribute = is_none(vessel.rs_number)
            case "imo":
                vessel_attribute = is_none(vessel.imo_number)
            case "power":
                vessel_attribute = is_none(vessel.me_power)
            case "gt":
                vessel_attribute = is_none(vessel.g_tonnage)
            case "bdate":
                vessel_attribute = is_none(vessel.build_date)
            case _:
                vessel_attribute = ""
    else:
        vessel_attribute = ""
    return vessel_attribute


def get_surveyor_or_none(surveyors_qs, specialty=None):
    """Получить инспектора из списка назначенных инспекторов по заявке."""
    if not surveyors_qs.exists():
        return ""
    surveyors = surveyors_qs.order_by("last_name").all()
    match specialty:
        case "hull":
            surveyor = f"{surveyors.first().last_name} {surveyors.first().first_name[0]}. {surveyors.first().patronymic_name[0]}."  # noqa: E501
        case "mech":
            if surveyors_qs.count() > 1:
                surveyor = f"{surveyors[1].last_name} {surveyors[1].first_name[0]}. {surveyors[1].patronymic_name[0]}."  # noqa: E501
            else:
                surveyor = f"{surveyors.first().last_name} {surveyors.first().first_name[0]}. {surveyors.first().patronymic_name[0]}."  # noqa: E501
        case _:
            if surveyors_qs.count() > 2:
                surveyor = f"{surveyors[2].last_name} {surveyors[2].first_name[0]}. {surveyors[2].patronymic_name[0]}."  # noqa: E501
            elif surveyors_qs.count() == 2:
                surveyor = f"{surveyors[1].last_name} {surveyors[1].first_name[0]}. {surveyors[1].patronymic_name[0]}."  # noqa: E501
            else:
                surveyor = f"{surveyors.last().last_name} {surveyors.last().first_name[0]}. {surveyors.last().patronymic_name[0]}."  # noqa: E501
    return surveyor


def is_product_survey(app, rs_branch, report_type):
    """Функция обработки поля document с параметрами материала или
    изделия при техническом наблюдении за их изготовлением."""
    if app.survey_code != Application.SurveyCode.C00015:  # noqa: E501
        if rs_branch not in RS_RU_BRANCHES:  # noqa: E501
            if (
                app.survey_code
                in [
                    Application.SurveyCode.C00001,
                    Application.SurveyCode.C00002,
                    Application.SurveyCode.C00003,
                    Application.SurveyCode.C00011,
                ]
                and report_type == ACCEPTANCE
            ):
                return f'{app} т/х {app.vessel} / m/v "{app.vessel.name_en}"'
            return app
        return str(app).split(" / ", maxsplit=1)[0]
    if app.documents is None:
        return ""
    if app.documents.count() == 1:
        return f"{app} {app.documents.first().item_particulars}"
    survey_scope = app
    for document in list(app.documents.all()):
        survey_scope = f"{str(survey_scope)} {document.item_particulars}, "
    survey_scope = survey_scope[:-2]
    return survey_scope


def get_authorized_person(person=None, rs_branch=None):
    """Получить уполномоченное лицо на русском или на
    русском и транслите в зависимости от филиала,
    если существует."""
    if person is not None:
        if person.phone_number != "" and person.email != "":  # type: ignore # noqa: E501
            if rs_branch in RS_RU_BRANCHES:
                authorized_person = f"{person}, {person.phone_number}, {person.email}"  # type: ignore # noqa: E501
            else:
                authorized_person = f"{person} / {translit(str(person), 'ru', reversed=True)}, {person.phone_number}, {person.email}"  # type: ignore # noqa: E501
        elif person.phone_number != "" and person.email == "":  # type: ignore # noqa: E501
            if rs_branch in RS_RU_BRANCHES:
                authorized_person = f"{person}, {person.phone_number}"  # type: ignore # noqa: E501
            else:
                authorized_person = f"{person} / {translit(str(person), 'ru', reversed=True)}, {person.phone_number}"  # type: ignore # noqa: E501
        elif person.phone_number == "" and person.email != "":  # type: ignore # noqa: E501
            if rs_branch in RS_RU_BRANCHES:
                authorized_person = f"{person}, {person.email}"  # type: ignore # noqa: E501
            else:
                authorized_person = f"{person} / {translit(str(person), 'ru', reversed=True)}, {person.email}"  # type: ignore # noqa: E501
        else:
            if rs_branch in RS_RU_BRANCHES:
                authorized_person = f"{person}"  # type: ignore
            else:
                authorized_person = f"{person} / {translit(str(person), 'ru', reversed=True)}"  # type: ignore # noqa: E501
    else:
        authorized_person = "--"
    return authorized_person


def is_legal_address_same(
    is_same_check, postal_address, rs_branch, legal_address=None
):  # noqa: E501
    """Проверка на совпадение почтового и юридического адресов."""
    if is_same_check is True:
        return get_port_or_address(postal_address, rs_branch)
    return get_port_or_address(legal_address, rs_branch)


def get_form_type_en(f_type):
    """Получить название формы документа на
    английском языке для двуязычных форм."""
    match f_type:
        case Form.FormType.AGR | Form.FormType.AGT:
            result = "Aggrement"
        case Form.FormType.ANN:
            result = "Annex"
        case Form.FormType.ATL:
            result = "According to list"
        case Form.FormType.CER:
            result = "Certificate"
        case Form.FormType.CHE:
            result = "Check-list"
        case Form.FormType.LET:
            result = "Letter of approval"
        case Form.FormType.MIN:
            result = "Minutes"
        case Form.FormType.QUR:
            result = "Ship's status"
        case Form.FormType.REC:
            result = "Record"
        case Form.FormType.REG:
            result = "Register"
        case Form.FormType.REP | Form.FormType.RPT:
            result = "Report"
        case _:
            return ""
    return result


def get_issued_docs(
    document_qs,
    survey_code=Application.SurveyCode.C00001,
    document_date=None,
    rs_branch=None,
):  # noqa: E501
    """Выданные документы в зависимости от кода услуги."""
    if not document_qs.exists():
        return "--"
    match survey_code:
        case (
            Application.SurveyCode.C00001
            | Application.SurveyCode.C00003
            | Application.SurveyCode.C00009
            | Application.SurveyCode.C00011
            | Application.SurveyCode.C00014
            | Application.SurveyCode.C00015
            | Application.SurveyCode.C00101
            | Application.SurveyCode.C00103
            | Application.SurveyCode.C00104
            | Application.SurveyCode.C00121
        ):  # noqa: E501
            if document_qs.count() > 1:
                if rs_branch in RS_RU_BRANCHES:
                    documents = f"{document_qs.first().form} №№ {document_qs.first()} - {document_qs.last()} от {is_none(document_date)}"  # noqa: E501
                else:
                    documents = f"{document_qs.first().form.get_form_type_display()} ф. / {get_form_type_en(document_qs.first().form.form_type)} of f. {document_qs.first().form.number} №№ {document_qs.first()} - {document_qs.last()} от/dd {is_none(document_date)}"  # noqa: E501
            else:
                if rs_branch in RS_RU_BRANCHES:
                    documents = f"{document_qs.first().form} № {document_qs.first()} от {is_none(document_date)}"  # noqa: E501
                else:
                    documents = f"{document_qs.first().form.get_form_type_display()} ф. / {get_form_type_en(document_qs.first().form.form_type)} of f. {document_qs.first().form.number} № {document_qs.first()} от/dd {is_none(document_date)}"  # noqa: E501
        case Application.SurveyCode.C00002:
            if rs_branch in RS_RU_BRANCHES:
                documents = f"({document_qs.first().form} {document_qs.first()})"  # type: ignore # noqa: E501
            else:
                documents = f"{document_qs.first().form.get_form_type_display()} № / {get_form_type_en(document_qs.first().form.form_type)} No. {document_qs.first()}"  # noqa: E501
        case Application.SurveyCode.C00006:
            if rs_branch in RS_RU_BRANCHES:
                documents = f"{document_qs.first().form} {document_qs.first()} от {is_none(document_date)}"  # type: ignore # noqa: E501
            else:
                documents = f"{document_qs.first().form.get_form_type_display()} № / {get_form_type_en(document_qs.first().form.form_type)} No. {document_qs.first()} от/dd {is_none(document_date)}"  # noqa: E501
        case _:
            return ""
    return documents


def moneyfmt(
    value, places=2, curr="", sep=",", dp=".", pos="", neg="-", trailneg=""
):  # noqa: E501
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    # taken from https://docs.python.org/3/library/decimal.html

    q = Decimal(10) ** -places  # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else "0")
    if places:
        build(dp)
    if not digits:
        build("0")
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return "".join(reversed(result))


def replace_dollar_by_rnb(curr_in_words_input):
    """Заменяет слово доллар или dollar на слово 'юань'."""
    separation = curr_in_words_input.split()
    result = ""
    new_list = []
    for item in separation:
        if item == "долларов":
            new_list.append("юаней")
            continue
        if item == "доллара":
            new_list.append("юаня")
            continue
        if item == "доллар":
            new_list.append("юань")
            continue
        if item in ["центов", "цента", "цент"]:
            new_list.append("цзяо")
            continue
        if item in ["dollars", "dollar"]:
            new_list.append("yuan")
            continue
        if item in ["cents", "cent"]:
            new_list.append("jiao")
            continue
        new_list.append(item)
    result = (" ").join(new_list)
    return result


def get_sum_in_words(netto: Decimal, currency_code, tax=None):
    """Сумма прописью: российский рубль, евро, доллар США,
    китайский юань, белорусский рубль."""
    VAT_RATE = 0.2
    vat = round(netto * Decimal(VAT_RATE), 2)
    brutto = round(netto + vat, 2)
    match currency_code:
        case BankAccount.Currency.RUB:
            netto_formatted = moneyfmt(netto, sep=" ", dp=",")
            vat_formatted = moneyfmt(vat, sep=" ", dp=",")
            brutto_formatted = moneyfmt(brutto, sep=" ", dp=",")
            if tax is None:
                result = f"{netto_formatted} p. ({num2words(netto, lang='ru', to='currency', separator='', cents=False, currency='RUB')})"  # noqa: E501
            elif tax == "vat":
                result = f"{vat_formatted} p. ({num2words(vat, lang='ru', to='currency', separator='', cents=False, currency='RUB')})"  # noqa: E501
            else:
                result = f"{brutto_formatted} p. ({num2words(brutto, lang='ru', to='currency', separator='', cents=False, currency='RUB')})"  # noqa: E501
        case BankAccount.Currency.EUR:
            netto_formatted = moneyfmt(netto, curr="€", sep=" ", dp=",")
            result = f"{netto_formatted} ({num2words(netto, lang='ru', to='currency', separator='', cents=False)} / {num2words(netto, to='currency', separator=' and', cents=False)})"  # noqa: E501
        case BankAccount.Currency.USD:
            netto_formatted = moneyfmt(netto, curr="$", sep=" ")
            result = f"{netto_formatted} ({num2words(netto, lang='ru', to='currency', separator='', cents=False, currency='USD')} / {num2words(netto, lang='en', to='currency', separator=' and', cents=False, currency='USD')})"  # noqa: E501
        # noqa: E501
        case BankAccount.Currency.CNY:
            netto_formatted = moneyfmt(netto, curr="¥", sep=" ")
            num_in_words_ru = num2words(
                netto,
                lang="ru",
                to="currency",
                separator="",
                cents=False,
                currency="USD",
            )
            num_in_words_en = num2words(
                netto,
                to="currency",
                separator=" and",
                cents=False,
                currency="USD",
            )
            result = f"{netto_formatted} ({replace_dollar_by_rnb(num_in_words_ru)} / {replace_dollar_by_rnb(num_in_words_en)})"  # noqa: E501ф
        case BankAccount.Currency.BYN:
            netto_formatted = moneyfmt(netto, sep=" ", dp=",")
            vat_formatted = moneyfmt(vat, sep=" ", dp=",")
            brutto_formatted = moneyfmt(brutto, sep=" ", dp=",")
            if tax is None:
                result = f"{netto_formatted} pуб. ({num2words(netto, lang='ru', to='currency', separator='', cents=False, currency='RUB')}"  # noqa: E501
            elif tax == "vat":
                result = f"{vat_formatted} pуб. ({num2words(vat, lang='ru', to='currency', separator='', cents=False, currency='RUB')}"  # noqa: E501
            else:
                result = f"{brutto_formatted} pуб. ({num2words(brutto, lang='ru', to='currency', separator='', cents=False, currency='RUB')}"  # noqa: E501
        case _:
            if tax is None:
                result = f"{netto}"
    return result


def get_month_en(app_date):
    """Получить название месяца на английском
    в зависимости от его номера."""
    month_no = dateformat.format(app_date, "n")
    match month_no:
        case "1":
            month_in_en = "January"
        case "2":
            month_in_en = "February"
        case "3":
            month_in_en = "March"
        case "4":
            month_in_en = "April"
        case "5":
            month_in_en = "May"
        case "6":
            month_in_en = "June"
        case "7":
            month_in_en = "July"
        case "8":
            month_in_en = "August"
        case "9":
            month_in_en = "September"
        case "10":
            month_in_en = "October"
        case "11":
            month_in_en = "November"
        case "12":
            month_in_en = "December"
        case _:
            month_in_en = "not set"
    return month_in_en


def get_port_or_address(port_or_address, rs_branch=None):
    """Возвращает город на русском или русско-
    английском в зависимости от филиала."""
    if port_or_address is not None:
        if rs_branch not in RS_RU_BRANCHES:
            return port_or_address
        return str(port_or_address).split(" / ", maxsplit=1)[0]
    return "--"


def get_register_staff_position(position, position_en, rs_branch):
    """Возвращает должности персонала РС на русском
    или русско-английском в зависимости от филиала."""
    if rs_branch in RS_RU_BRANCHES:
        return position
    return f"{position} / {position_en}"


def get_register_signer_proxy(poa_number, poa_date, rs_branch):
    """Функция определения доверенности подписанта от РС на русском
    языке и двуязычной форме в зависимости от филиала."""
    if rs_branch in RS_RU_BRANCHES:
        return f"Доверенности № {poa_number} от {is_none(poa_date)}"
    return f"Доверенности / Power of attorney № {poa_number} от/dd {is_none(poa_date)}"  # noqa: E501


def get_signer(
    firstname,
    lastname,
    rs_branch,
    is_register,
    middlename=None,
    firstname_en=None,
    lastname_en=None,
):  # noqa: E501
    """Получить имя заявителя или представителя РС для одноязычных или
    транслитерацию для двуязычных форм в зависимости от расположения
    филиала."""
    if rs_branch in RS_RU_BRANCHES:
        if middlename is None:
            return f"{firstname[0]}. {lastname} "  # type: ignore # noqa: E501
        return f"{firstname[0]}. {middlename[0]}. {lastname}"  # type: ignore # noqa: E501
    if is_register is False:
        if detect_language(lastname) != "ru":
            if middlename is None:
                return f"{firstname[0]}. {lastname}"  # noqa: E501
            return f"{firstname[0]}. {middlename[0]}. {lastname}"  # noqa: E501
        if middlename is None:
            return f"{firstname[0]}. {lastname} / {translit(firstname[0], 'ru', reversed=True)}. {translit(lastname, 'ru', reversed=True)}"  # noqa: E501
        return f"{firstname[0]}. {middlename[0]}. {lastname} / {translit(firstname[0], 'ru', reversed=True)}. {translit(middlename[0], 'ru', reversed=True)}. {translit(lastname, 'ru', reversed=True)}"  # noqa: E501
    return f"{firstname[0]}. {middlename[0]}. {lastname} / {firstname_en[0]}. {lastname_en}"  # type: ignore # noqa: E501


def get_surveyor_or_applicant(
    position,
    lastname,
    firstname,
    middlename=None,
    rs_branch=None,
    position_en=None,
    is_register=False,
    firstname_en=None,
    lastname_en=None,
):  # noqa: E501
    """Получить имя и должность заявителя или представителя РС в
    именительном падеже и их перевод на английский язык (транслитерацию)
    для двуязычных форм в зависимости от расположения филиала."""
    if rs_branch in RS_RU_BRANCHES:
        if middlename is None:
            return f"{position} {lastname} {firstname[0]}."  # type: ignore # noqa: E501
        return f"{position} {lastname} {firstname[0]}. {middlename[0]}."  # type: ignore # noqa: E501
    if is_register is False:
        if detect_language(lastname) != "ru":
            if middlename is None:
                return f"{position}/{position_en} {GONORATIVE} {firstname[0]}. {lastname}"  # noqa: E501
            return f"{position}/{position_en} {GONORATIVE} {firstname[0]}. {middlename[0]}. {lastname}"  # noqa: E501
        if middlename is None:
            return f"{position} {lastname} {firstname[0]}. / {position_en} {translit(firstname[0], 'ru', reversed=True)}. {translit(lastname, 'ru', reversed=True)}"  # noqa: E501
        return f"{position} {lastname} {firstname[0]}. {middlename[0]}. / {position_en} {translit(firstname[0], 'ru', reversed=True)}. {translit(middlename[0], 'ru', reversed=True)}. {translit(lastname, 'ru', reversed=True)}"  # noqa: E501
    return f"{position} {lastname} {firstname[0]}. {middlename[0]}. / {position_en} {firstname_en[0]}. {lastname_en}"  # type: ignore # noqa: E501


def get_survey_object_en(survey_object_value):
    """Получить перевод объектов освидетельствования
    на английский язык для двуязычных форм."""
    match survey_object_value:
        case Application.SurveyObject.SHIPPART:
            result = "The ship"
        case Application.SurveyObject.ALLPARTS:
            result = "The ship on all parts"
        case Application.SurveyObject.HULLPART:
            result = "The ship on the hull part"
        case Application.SurveyObject.MECHPART:
            result = "The ship on the mechanical part"
        case Application.SurveyObject.ELECPART:
            result = "The ship on the electric-mechanical parts"
        case Application.SurveyObject.HULLMECH:
            result = "The ship on the hull and mechanical parts"
        case Application.SurveyObject.MECHELEC:
            result = (
                "The ship on the mechanical and electric-mechanical parts"  # noqa: E501
            )
        case Application.SurveyObject.RADIPART:
            result = "The ship on the radio part"  # noqa: E501
        case _:
            return ""
    return result


def get_survey_object(ship_part_value, ship_part_label, branch_number):
    """Получить объекты освидетельствования судна на
    одном или двух языках в зависимости от филиала."""
    if branch_number in RS_RU_BRANCHES:
        result = ship_part_label
    else:
        result = (
            f"{ship_part_label} / {get_survey_object_en(ship_part_value)}"  # noqa: E501
        )
    return result


def print_docs(request, **kwargs):
    """Функция печати документов."""

    company = get_object_or_404(Company, slug=kwargs["slug"])
    application = get_object_or_404(Application, id=kwargs["pk"])
    branch_number = application.register_signer.office_number.number[0:3]  # type: ignore # noqa: E501
    rs_branch = (
        Company.objects.filter(
            name__icontains=RS_BRANCH_NAME_FIRST_CHARS
        ).filter(  # noqa: E501
            responsible_offices__number__icontains=branch_number
        )  # noqa: E501
    ).first()

    button_name = request.GET.get("name")
    docx_template = get_docx_template(
        application.survey_code,
        button_name,
        branch_number,
        application.survey_scope,
    )
    doc = DocxTemplate(f"templates/docx/{docx_template}")
    context = {
        # for agreement-applications
        "application": application.number,
        "day": application.date.strftime("%d"),  # type: ignore
        "month": dateformat.format(application.date, settings.DATE_FORMAT),
        "year": application.date.strftime("%y"),  # type: ignore
        "vessel": is_vessel_none(application.vessel, "name", branch_number),  # type: ignore # noqa: E501
        "rs_number": is_vessel_none(application.vessel, "rs"),  # type: ignore # noqa: E501
        "imo_number": is_vessel_none(application.vessel, "imo"),  # type: ignore # noqa: E501
        "survey_scope": is_product_survey(
            application, branch_number, button_name
        ),  # noqa: E501
        "survey_object": get_survey_object(application.survey_object, application.get_survey_object_display(), branch_number),  # type: ignore # noqa: E501
        "city": get_port_or_address(application.city, branch_number),
        "date": application.date.strftime("%d.%m.%Y"),
        "company": company,
        "applicant": get_signer_cased(application.applicant_signer.position, application.applicant_signer.second_name, application.applicant_signer.first_name, application.applicant_signer.patronymic_name, branch_number, application.applicant_signer.position_en),  # type: ignore # noqa: E501
        "applicant_proxy": get_genitive_case_proxy(application.applicant_signer.proxy_type, application.applicant_signer.get_proxy_type_display(), application.applicant_signer.proxy_number, application.applicant_signer.proxy_date, branch_number),  # type: ignore # noqa: E501
        "authorized_person": get_authorized_person(application.authorized_person, branch_number),  # type: ignore # noqa: E501
        "previous_survey_place": get_port_or_address(application.vesselextrainfo.city, branch_number),  # type: ignore # noqa: E501
        "previous_survey_date": is_none(application.vesselextrainfo.previous_survey_date),  # type: ignore # noqa: E501
        "last_psc_inspection": f"{is_none(application.vesselextrainfo.last_psc_inspection_date)} {is_none(application.vesselextrainfo.last_psc_inspection_result)}",  # type: ignore # noqa: E501
        "currency": company.bank_accounts.filter(current_bankaccount=True).first().account_currency,  # type: ignore # noqa: E501
        "postal_address_rs": rs_branch.addresses.first(),  # type: ignore # noqa: E501
        "legal_address_rs": is_legal_address_same(rs_branch.addresses.first().is_same, rs_branch.addresses.first(), branch_number, rs_branch.addresses.last()),  # type: ignore # noqa: E501
        "inn_rs": is_none(rs_branch.inn),  # type: ignore
        "kpp_rs": is_none(rs_branch.kpp),  # type: ignore
        "ogrn_rs": is_none(rs_branch.ogrn),  # type: ignore
        "phone_number_rs": is_none(rs_branch.phone_number),  # type: ignore
        "email_rs": is_none(rs_branch.email),  # type: ignore
        "payment_account_rs": rs_branch.bank_accounts.first(),  # type: ignore # noqa: E501
        "postal_address": get_port_or_address(company.addresses.first(), branch_number),  # type: ignore # noqa: E501
        "legal_address": is_legal_address_same(company.addresses.first().is_same, company.addresses.first(), branch_number, company.addresses.last()),  # type: ignore # noqa: E501
        "inn": is_none(company.inn),
        "kpp": is_none(company.kpp),
        "ogrn": is_none(company.ogrn),
        "phone_number": is_none(company.phone_number),
        "email": is_none(company.email),
        "payment_account": company.bank_accounts.filter(current_bankaccount=True).first(),  # type: ignore # noqa: E501
        "register": get_signer_cased(application.register_signer.position, application.register_signer.last_name, application.register_signer.first_name, application.register_signer.patronymic_name, branch_number, application.register_signer.position.name_en, True, application.register_signer.first_name_en, application.register_signer.last_name_en),  # type: ignore # noqa: E501
        "register_signer_position": get_register_staff_position(application.register_signer.position, application.register_signer.position.name_en, branch_number),  # type: ignore # noqa: E501
        "register_signer_proxy": get_register_signer_proxy(application.register_signer.proxy_number, application.register_signer.proxy_date, branch_number),  # type: ignore # noqa: E501
        "register_signer": get_signer(application.register_signer.first_name, application.register_signer.last_name, branch_number, True, application.register_signer.patronymic_name, application.register_signer.first_name_en, application.register_signer.last_name_en),  # type: ignore # noqa: E501
        "applicant_signer": get_signer(application.applicant_signer.first_name, application.applicant_signer.second_name, branch_number, False, application.applicant_signer.patronymic_name),  # type: ignore # noqa: E501
        # for small crafts
        "engine_power": str(is_vessel_none(application.vessel, "power")),  # type: ignore # noqa: E501
        "vessel_departure_estimated_date": is_none(application.vesselextrainfo.completion_expected_date),  # type: ignore # noqa: E501
        "rs_branch_city": rs_branch.addresses.first().city,  # type: ignore # noqa: E501
        # for reports on acceptance-delivery services
        "surveyor": get_surveyor_or_applicant(
            request.user.position,
            request.user.last_name,
            request.user.first_name,
            request.user.patronymic_name,
            branch_number,
            request.user.position.name_en,
            True,
            request.user.first_name_en,
            request.user.last_name_en,
        ),  # noqa: E501
        "surveyor_proxy": get_register_signer_proxy(request.user.proxy_number, request.user.proxy_date, branch_number),  # type: ignore # noqa: E501
        "applicant_nominative": get_surveyor_or_applicant(application.applicant_signer.position, application.applicant_signer.second_name, application.applicant_signer.first_name, application.applicant_signer.patronymic_name, branch_number, application.applicant_signer.position_en),  # type: ignore # noqa: E501
        "issued_docs": get_issued_docs(application.documents, application.survey_code, application.completion_date, branch_number),  # type: ignore # noqa: E501
        "service_cost": get_sum_in_words(application.account.service_cost, company.bank_accounts.filter(current_bankaccount=True).first().account_currency),  # type: ignore # noqa: E501
        "tax": get_sum_in_words(application.account.service_cost, company.bank_accounts.filter(current_bankaccount=True).first().account_currency, "vat"),  # type: ignore # noqa: E501
        "total": get_sum_in_words(application.account.service_cost, company.bank_accounts.filter(current_bankaccount=True).first().account_currency, "total"),  # type: ignore # noqa: E501
        # "surveyor_signer": f"{request.user.first_name[0]}. {request.user.patronymic_name[0]}. {request.user.last_name}",  # type: ignore # noqa: E501
        "surveyor_signer": get_signer(request.user.first_name, request.user.last_name, branch_number, True, request.user.patronymic_name, request.user.first_name_en, request.user.last_name_en),  # type: ignore # noqa: E501
        # for document checking sheet
        "completion_date": is_none(application.completion_date),
        "g_tonnage": str(is_vessel_none(application.vessel, "gt")),  # type: ignore # noqa: E501
        "build_date": str(is_vessel_none(application.vessel, "bdate")),  # type: ignore # noqa: E501
        "hull_surveyor": get_surveyor_or_none(application.vesselextrainfo.assigned_surveyors, "hull"),  # type: ignore # noqa: E501
        "mech_surveyor": get_surveyor_or_none(application.vesselextrainfo.assigned_surveyors, "mech"),  # type: ignore # noqa: E501
        "elrn_surveyor": get_surveyor_or_none(application.vesselextrainfo.assigned_surveyors, "elrn"),  # type: ignore # noqa: E501
        # for bilingual forms
        "month_en": get_month_en(application.date),
        "city_ru": get_port_or_address(application.city, "121"),
        "city_en": str(application.city).split(" / ", maxsplit=1)[1],
    }  # noqa: E501

    doc.render(context)
    doc.save(f"templates/docx/saved/{docx_template}")

    doc_io = io.BytesIO()  # create a file-like object
    doc.save(doc_io)  # save data to file-like object
    doc_io.seek(0)  # go to the beginning of the file-like object

    response = HttpResponse(doc_io.read())

    # Content-Disposition header makes a file downloadable
    response["Content-Disposition"] = (
        f"attachment; filename={docx_template}"  # noqa: E501
    )

    # Set the appropriate Content-Type for docx file
    response["Content-Type"] = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # noqa: E501
    )
    return response
