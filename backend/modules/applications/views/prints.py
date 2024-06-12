# pylint: disable=line-too-long, unused-variable, redefined-builtin, invalid-name, too-many-arguments, too-many-branches, too-many-locals, too-many-statements  # noqa: E501
"""Представления для модели applications."""

import io
from decimal import Decimal
import datetime
import pymorphy3
from petrovich.main import Petrovich
from petrovich.enums import Case
from num2words import num2words
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import dateformat
from docxtpl import DocxTemplate
from ..models import (
    Application,
    Company,
)

User = get_user_model()


def get_docx_template(survey_code, report_type, rs_branch, survey_scope=None):  # noqa: E501
    """Получить определённый шаблон docx в зависимости
       от кода услуги и подразделения."""
    # report_type is certificate on AGREEMENT-application or
    # ACCEPTANCE of delivery service report
    # SHEET is document check sheet
    print(rs_branch)
    # if rs_branch in ["110", "112", "120", "121", "125", "130", "131", "141", "150", "170", "171", "172", "173", "174", "184", "190"]:  # noqa: E501
    match survey_code:
        case "00001" | "00003" | "00011":
            if report_type == "agreement":
                template = "810_1_1.docx"
            elif report_type == "acceptance":
                template = "430_3_4.docx"
            else:
                template = "List_registratsii_proverki_dokumentov.docx"
        case "00006":
            if report_type == "agreement":
                template = "810_1_11.docx"
            else:
                template = "430_3_1.docx"
        case "00015":
            if report_type == "agreement":
                template = "810_1_2_p.docx"
            else:
                template = "430_3_3.docx"
        case "00101":
            if report_type == "agreement":
                template = "810_1_2_w.docx"
            else:
                template = "430_3_1.docx"
        case "00103":
            if report_type == "agreement":
                template = "810_1_2_s.docx"
            else:
                template = "430_3_1.docx"
        case "00121":
            if report_type == "agreement":
                if survey_scope == "I":
                    template = "810_1_10.docx"
                else:
                    template = "810_1_10_1.docx"
            elif report_type == "acceptance":
                template = "430_3_4.docx"
            else:
                template = "List_registratsii_proverki_dokumentov.docx"
        case _:
            # создать логику вывода сообщения на экран или все шаблоны сделать
            template = "404_page.docx"
    return template


def get_genitive_case(phrase):
    """Функция перевода слов в родительный падеж."""
    # parse a phrase with several words without punctuation, conj and prepos
    morph = pymorphy3.MorphAnalyzer()
    result = ' '.join(morph.parse(word)[0].inflect({'gent'}).word for word in phrase.split())  # type: ignore # noqa: E501
    return result


def get_genitive_case_lastname(lastname):
    """Функция перевода фамилий в родительный падеж."""
    # to fix the bug with a last name see link below:
    # https://github.com/damirazo/Petrovich/issues/8
    p = Petrovich()
    cased_lname = p.lastname(lastname, Case.GENITIVE)
    return cased_lname


def get_genitive_case_proxy(proxy, number=None, date=None):
    """Функция перевода названий документов,
       на основании которых действует заявитель,
       в родительный падеж."""
    match proxy:
        case "Устав":
            power_of_attoney_gen = "Устава"
        case "Кодекс торгового мореплавания (КТМ РФ)":
            power_of_attoney_gen = "Кодекса торгового мореплавания (КТМ РФ)"
        case "Доверенность":
            power_of_attoney_gen = f"Доверенности № {number} от {is_none(date)}"  # type: ignore # noqa: E501
        case "Приказ":
            power_of_attoney_gen = "Приказа"
        case "Свидетельство о регистрации":
            power_of_attoney_gen = "Свидетельства о регистрации"
        case _:
            power_of_attoney_gen = proxy
    return power_of_attoney_gen


def is_none(value):
    """Проверка значений на None."""
    if value is not None:
        if isinstance(value, datetime.date):
            return value.strftime("%d.%m.%Y")
        return value
    return "--"


def is_vessel_none(vessel=None, argument=None, rs_branch=None):  # noqa: E501
    """Проверка судна на None для заявок в промышленности."""
    if vessel is not None:
        match argument:
            case "name":
                if vessel.flag != "RU" or rs_branch in ["110", "112", "120", "121", "125", "130", "131", "141", "150", "170", "171", "172", "173", "174", "184", "190"]:  # noqa: E501
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
    surveyors = surveyors_qs.all()
    match specialty:
        case "hull":
            surveyor = f"{surveyors_qs.first().last_name} {surveyors_qs.first().first_name[0]}. {surveyors_qs.first().patronymic_name[0]}."  # noqa: E501
        case "mech":
            if surveyors_qs.count() > 1:
                surveyor = f"{surveyors[1].last_name} {surveyors[1].first_name[0]}. {surveyors[1].patronymic_name[0]}."  # noqa: E501
            else:
                surveyor = f"{surveyors_qs.first().last_name} {surveyors_qs.first().first_name[0]}. {surveyors_qs.first().patronymic_name[0]}."  # noqa: E501
        case _:
            if surveyors_qs.count() > 2:
                surveyor = f"{surveyors[2].last_name} {surveyors[2].first_name[0]}. {surveyors[2].patronymic_name[0]}."  # noqa: E501
            elif surveyors_qs.count() == 2:
                surveyor = f"{surveyors[1].last_name} {surveyors[1].first_name[0]}. {surveyors[1].patronymic_name[0]}."  # noqa: E501
            else:
                surveyor = f"{surveyors_qs.last().last_name} {surveyors_qs.last().first_name[0]}. {surveyors_qs.last().patronymic_name[0]}."  # noqa: E501
    return surveyor


def is_product_survey(app):
    """Функция обработки поля document с параметрами материала или
       изделия при техническом наблюдении за их изготовлением."""
    if app.survey_code != "00015":
        return app
    if app.documents is None:
        return ""
    if app.documents.count() == 1:
        return f"{app} {app.documents.first().item_particulars}"
    survey_scope = app
    for document in list(app.documents.all()):
        survey_scope = f"{str(survey_scope)} {document.item_particulars}, "
    survey_scope = survey_scope[:-2]
    return survey_scope


def is_authorized_person_none(person=None):
    """Проверка уполномоченного лица на None."""
    if person is not None:
        if person.phone_number is not None and person.email is not None:  # type: ignore # noqa: E501
            authorized_person = f"{person}, {person.phone_number}, {person.email}"  # type: ignore # noqa: E501
        elif person.phone_number is not None and person.email is None:  # type: ignore # noqa: E501
            authorized_person = f"{person}, {person.phone_number}"  # type: ignore # noqa: E501
        elif person.phone_number is None and person.email is not None:  # type: ignore # noqa: E501
            authorized_person = f"{person}, {person.email}"  # type: ignore # noqa: E501
        else:
            authorized_person = f"{person}"  # type: ignore
    else:
        authorized_person = "--"
    return authorized_person


def is_legal_address_same(is_same_check, postal_address, legal_address=None):
    """Проверка на совпадение почтового и юридического адресов."""
    if is_same_check is True:
        return postal_address
    return legal_address


def get_issued_docs(document_qs, survey_code="00001", document_date=None):
    """Выданные документы в зависимости от кода услуги."""
    if not document_qs.exists():
        return ""
    match survey_code:
        case "00001" | "00003" | "00011" | "00015" | "00101" | "00103" | "00121":  # noqa: E501
            if document_qs.count() > 1:
                documents = f"{document_qs.first().form} №№ {document_qs.first()} - {document_qs.last()} от {is_none(document_date)}"  # noqa: E501
            else:
                documents = f"{document_qs.first().form} № {document_qs.first()} от {is_none(document_date)}"  # noqa: E501
        case "00006":
            documents = f"{document_qs.first().form} {document_qs.first()} от {is_none(document_date)}"  # type: ignore # noqa: E501
        case _:
            return ""
    return documents


def moneyfmt(value, places=2, curr='', sep=',', dp='.',
             pos='', neg='-', trailneg=''):
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

    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    if places:
        build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))


def get_sum_in_words(netto: Decimal, currency_code, tax=None):
    """Сумма прописью: российский рубль, евро, доллар США,
       китайский юань, белорусский рубль."""
    VAT_RATE = 0.2
    vat = round(netto * Decimal(VAT_RATE), 2)
    brutto = round(netto + vat, 2)
    match currency_code:
        case "RUB":
            netto_formatted = moneyfmt(netto, sep=' ', dp=',')
            vat_formatted = moneyfmt(vat, sep=' ', dp=',')
            brutto_formatted = moneyfmt(brutto, sep=' ', dp=',')
            if tax is None:
                result = f"{netto_formatted} p. ({num2words(netto, lang='ru', to='currency', separator='', cents=False, currency='RUB')})"  # noqa: E501
            elif tax == "vat":
                result = f"{vat_formatted} p. ({num2words(vat, lang='ru', to='currency', separator='', cents=False, currency='RUB')})"  # noqa: E501
            else:
                result = f"{brutto_formatted} p. ({num2words(brutto, lang='ru', to='currency', separator='', cents=False, currency='RUB')})"  # noqa: E501
        case "EUR":
            netto_formatted = moneyfmt(netto, curr='€', sep=' ', dp=',')
            vat_formatted = moneyfmt(vat, curr='€', sep=' ', dp=',')
            brutto_formatted = moneyfmt(brutto, curr='€', sep=' ', dp=',')
            if tax is None:
                result = f"{netto_formatted} ({num2words(netto, to='currency', separator=' and', cents=False)})"  # noqa: E501
            elif tax == "vat":
                result = f"{vat_formatted} ({num2words(vat, to='currency', separator=' and', cents=False)})"  # noqa: E501
            else:
                result = f"{brutto_formatted} ({num2words(brutto, to='currency', separator=' and', cents=False)})"  # noqa: E501
        case "USD":
            netto_formatted = moneyfmt(netto, curr='$', sep=' ')
            vat_formatted = moneyfmt(vat, curr='$', sep=' ')
            brutto_formatted = moneyfmt(brutto, curr='$', sep=' ')
            if tax is None:
                result = f"{netto_formatted} ({num2words(netto, lang='en', to='currency', separator=' and', cents=False, currency='USD')})"  # noqa: E501
            elif tax == "vat":
                result = f"{vat_formatted} ({num2words(vat, lang='en', to='currency', separator=' and', cents=False, currency='USD')})"  # noqa: E501
            else:
                result = f"{brutto_formatted} ({num2words(brutto, lang='en', to='currency', separator=' and', cents=False, currency='USD')})"  # noqa: E501
        case "CNY":
            netto_formatted = moneyfmt(netto, curr='¥', sep=' ')
            vat_formatted = moneyfmt(vat, curr='¥', sep=' ')
            brutto_formatted = moneyfmt(brutto, curr='¥', sep=' ')
            if tax is None:
                result = f"{netto} ({num2words(netto, to='currency', separator=' and', cents=False)})"  # noqa: E501
            elif tax == "vat":
                result = f"{vat} ({num2words(vat, to='currency', separator=' and', cents=False)})"  # noqa: E501
            else:
                result = f"{brutto} ({num2words(brutto, to='currency', separator=' and', cents=False)})"  # noqa: E501
        case "BYN":
            netto_formatted = moneyfmt(netto, sep=' ', dp=',')
            vat_formatted = moneyfmt(vat, sep=' ', dp=',')
            brutto_formatted = moneyfmt(brutto, sep=' ', dp=',')
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


def print_docs(request, **kwargs):
    """Функция печати документов."""

    company = get_object_or_404(Company, slug=kwargs["slug"])
    application = get_object_or_404(Application, id=kwargs["pk"])
    branch_number = application.register_signer.office_number.number[0:3]  # type: ignore # noqa: E501
    rs_branch = (
        Company.objects.filter(name__icontains="РС,").filter(
            responsible_offices__number__icontains=branch_number
        )  # noqa: E501
    ).first()

    button_name = request.GET.get('name')
    docx_template = get_docx_template(application.survey_code, button_name, branch_number, application.survey_scope)  # noqa: E501
    doc = DocxTemplate(f"templates/docx/{docx_template}")

    context = {
        # for agreement-applications
        "application": application.number,
        "day": application.date.strftime("%d"),  # type: ignore
        "month": dateformat.format(application.date, settings.DATE_FORMAT),
        "year": application.date.strftime("%y"),  # type: ignore
        "vessel": is_vessel_none(application.vessel, "name",  branch_number),  # type: ignore # noqa: E501
        "rs_number": is_vessel_none(application.vessel, "rs"),  # type: ignore # noqa: E501
        "imo_number": is_vessel_none(application.vessel, "imo"),  # type: ignore # noqa: E501
        "survey_scope": is_product_survey(application),
        "survey_object": application.get_survey_object_display(),  # type: ignore # noqa: E501
        "city": application.city,
        "date": application.date.strftime("%d.%m.%Y"),
        "company": company,
        "applicant": f"{get_genitive_case(application.applicant_signer.position)} {get_genitive_case_lastname(application.applicant_signer.second_name)} {application.applicant_signer.first_name[0]}. {application.applicant_signer.patronymic_name[0]}.",  # type: ignore # noqa: E501
        "applicant_proxy": get_genitive_case_proxy(application.applicant_signer.get_proxy_type_display(), application.applicant_signer.proxy_number, application.applicant_signer.proxy_date),  # type: ignore # noqa: E501
        "authorized_person": is_authorized_person_none(application.authorized_person),  # type: ignore # noqa: E501
        "previous_survey_place": is_none(application.vesselextrainfo.city),  # type: ignore # noqa: E501
        "previous_survey_date": is_none(application.vesselextrainfo.previous_survey_date),  # type: ignore # noqa: E501
        "last_psc_inspection": f"{is_none(application.vesselextrainfo.last_psc_inspection_date)} {is_none(application.vesselextrainfo.last_psc_inspection_result)}",  # type: ignore # noqa: E501
        "currency": company.bank_accounts.filter(current_bankaccount=True).first().account_currency,  # type: ignore # noqa: E501
        "postal_address_rs": rs_branch.addresses.first(),  # type: ignore # noqa: E501
        "legal_address_rs": is_legal_address_same(rs_branch.addresses.first().is_same, rs_branch.addresses.first(), rs_branch.addresses.last()),  # type: ignore # noqa: E501
        "inn_rs": is_none(rs_branch.inn),  # type: ignore
        "kpp_rs": is_none(rs_branch.kpp),  # type: ignore
        "ogrn_rs": is_none(rs_branch.ogrn),  # type: ignore
        "phone_number_rs": is_none(rs_branch.phone_number),  # type: ignore
        "email_rs": is_none(rs_branch.email),  # type: ignore
        "payment_account_rs": rs_branch.bank_accounts.first(),  # type: ignore # noqa: E501
        "postal_address": company.addresses.first(),  # type: ignore # noqa: E501
        "legal_address": is_legal_address_same(company.addresses.first().is_same, company.addresses.first(), company.addresses.last()),  # type: ignore # noqa: E501
        "inn": is_none(company.inn),
        "kpp": is_none(company.kpp),
        "ogrn": is_none(company.ogrn),
        "phone_number": is_none(company.phone_number),
        "email": is_none(company.email),
        "payment_account": company.bank_accounts.filter(current_bankaccount=True).first(),  # type: ignore # noqa: E501
        "register": f"{get_genitive_case(application.register_signer.position.name)} {get_genitive_case_lastname(application.register_signer.last_name)} {application.register_signer.first_name[0]}. {application.register_signer.patronymic_name[0]}.",  # type: ignore # noqa: E501
        "register_signer_position": application.register_signer.position,  # type: ignore # noqa: E501
        "register_signer_proxy": f"Доверенности № {application.register_signer.proxy_number} от {application.register_signer.proxy_date.strftime("%d.%m.%Y")}",  # type: ignore # noqa: E501
        "register_signer": f"{application.register_signer.first_name[0]}. {application.register_signer.patronymic_name[0]}. {application.register_signer.last_name}",  # type: ignore # noqa: E501
        "applicant_signer": f"{application.applicant_signer.first_name[0]}. {application.applicant_signer.patronymic_name[0]}. {application.applicant_signer.second_name}",  # type: ignore # noqa: E501
        # for small crafts
        "engine_power": str(is_vessel_none(application.vessel, "power")),  # type: ignore # noqa: E501
        "vessel_departure_estimated_date": is_none(application.vesselextrainfo.completion_expected_date),  # type: ignore # noqa: E501
        "rs_branch_city": rs_branch.addresses.first().city,  # type: ignore # noqa: E501
        # for reports on acceptance-delivery services
        "surveyor": f"{request.user.position} {request.user.last_name} {request.user.first_name[0]}. {request.user.patronymic_name[0]}.",  # noqa: E501
        "surveyor_proxy": f"Доверенности № {request.user.proxy_number} от {request.user.proxy_date.strftime("%d.%m.%Y")}",  # type: ignore # noqa: E501
        "applicant_nominative": f"{application.applicant_signer.position} {application.applicant_signer.second_name} {application.applicant_signer.first_name[0]}. {application.applicant_signer.patronymic_name[0]}.",  # type: ignore # noqa: E501
        "issued_docs": get_issued_docs(application.documents, application.survey_code, application.completion_date),  # type: ignore # noqa: E501
        "service_cost": get_sum_in_words(application.account.service_cost, company.bank_accounts.filter(current_bankaccount=True).first().account_currency),  # type: ignore # noqa: E501
        "tax": get_sum_in_words(application.account.service_cost, company.bank_accounts.filter(current_bankaccount=True).first().account_currency, "vat"),  # type: ignore # noqa: E501
        "total": get_sum_in_words(application.account.service_cost, company.bank_accounts.filter(current_bankaccount=True).first().account_currency, "total"),  # type: ignore # noqa: E501
        "surveyor_signer": f"{request.user.first_name[0]}. {request.user.patronymic_name[0]}. {request.user.last_name}",  # type: ignore # noqa: E501
        # for document checking sheet
        "completion_date": is_none(application.completion_date),
        "g_tonnage": str(is_vessel_none(application.vessel, "gt")),  # type: ignore # noqa: E501
        "build_date": str(is_vessel_none(application.vessel, "bdate")),  # type: ignore # noqa: E501
        "hull_surveyor": get_surveyor_or_none(application.vesselextrainfo.assigned_surveyors, "hull"),  # type: ignore # noqa: E501
        "mech_surveyor": get_surveyor_or_none(application.vesselextrainfo.assigned_surveyors, "mech"),  # type: ignore # noqa: E501
        "elrn_surveyor": get_surveyor_or_none(application.vesselextrainfo.assigned_surveyors, "elrn"),  # type: ignore # noqa: E501
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
