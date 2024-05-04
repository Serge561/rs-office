# pylint: disable=line-too-long, unused-argument, too-many-ancestors, too-few-public-methods, invalid-name, too-many-branches, unused-variable, redefined-builtin, too-many-arguments, too-many-locals, too-many-statements  # noqa: E501
"""Представления для модели applications."""

import io
from decimal import Decimal
import datetime
import pymorphy3
from petrovich.main import Petrovich
from petrovich.enums import Case
from num2words import num2words
from dal import autocomplete
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import dateformat

from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)
from docxtpl import DocxTemplate

from .forms import (
    AccountUpdateForm,
    ApplicationCreateForm,
    ApplicationUpdateForm,
    DocumentCreateForm,
    DocumentUpdateForm,
    FormCreateForm,
    VesselCreateForm,
    VesselExtraInfoUpdateForm,
)

# from django.contrib.postgres.search import (
#     SearchVector,
#     SearchQuery,
#     SearchRank,
# )  # noqa: E501
# from django.urls import reverse_lazy
from .models import (
    Account,
    Application,
    Company,
    Document,
    Form,
    Vessel,
    VesselExtraInfo,
)


User = get_user_model()


class VesselAutocomplete(autocomplete.Select2QuerySetView):
    """Автозаполнение для поля суда."""

    def get_queryset(self):
        qs = Vessel.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class ApplicationListView(LoginRequiredMixin, ListView):
    """Представления для вывода списка заявок."""

    model = Application
    template_name = "applications/application_list.html"
    login_url = "login"
    context_object_name = "applications"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return queryset.filter(company=company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Список заявок компании"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        return context


class ApplicationDetailView(DetailView):
    """Представление для вывода заявки компании."""

    model = Application
    template_name = "applications/application_detail.html"
    context_object_name = "application"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Заявка № {self.object.number} от {self.object.date:%d.%m.%Y}"  # type: ignore # noqa: E501
        return context


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    """Представление добавления заявки компании."""

    model = Application
    template_name = "applications/application_create.html"
    form_class = ApplicationCreateForm
    login_url = "login"

    def get_initial(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        user = self.request.user
        branch_number = user.office_number.number[0:3]  # type: ignore
        director = (
            User.objects.filter(position__name__icontains="директор").filter(
                office_number__number__icontains=branch_number
            )  # noqa: E501
        ).first()
        office_number = director.office_number.id  # type: ignore
        initial = {"company": company, "office_number": office_number}
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить заявку компании"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        return context

    def form_valid(self, form):
        """Автосохранение поля application."""
        instance = form.save(commit=False)
        form.instance.created_by = self.request.user
        form.instance.company = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        instance.save()
        return super().form_valid(form)


class ApplicationUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, UpdateView
):  # noqa: E501
    """Представление обновления заявки компании."""

    model = Application
    template_name = "applications/application_update.html"
    context_object_name = "application"
    form_class = ApplicationUpdateForm
    login_url = "login"
    success_message = "Заявка компании была успешно обновлена"

    def get_initial(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        user = self.request.user
        branch_number = user.office_number.number[0:3]  # type: ignore
        director = (
            User.objects.filter(position__name__icontains="директор").filter(
                office_number__number__icontains=branch_number
            )  # noqa: E501
        ).first()
        office_number = director.office_number.id  # type: ignore
        initial = {"company": company, "office_number": office_number}
        return initial

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["title"] = "Редактировать заявку компании"
        return context

    def form_valid(self, form):
        form.instance.updated_by = self.request.user  # type: ignore
        form.instance.company = get_object_or_404(  # type: ignore
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        form.save()  # type: ignore
        return super().form_valid(form)


class VesselCreateView(LoginRequiredMixin, CreateView):
    """Представление добавления судна."""

    model = Vessel
    template_name = "applications/vessels/vessel_create.html"
    form_class = VesselCreateForm
    login_url = "login"

    def get_success_url(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return reverse_lazy(
            "application_create", kwargs={"slug": company.slug}
        )  # noqa: E501

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавление судна"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        return context

    def form_valid(self, form):
        """Автосохранение поля company."""
        instance = form.save(commit=False)
        form.instance.created_by = self.request.user
        form.instance.company = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        instance.save()
        return super().form_valid(form)


# ================ функционал VesselExtraInfo ==================


# class VesselExtraInfoCreateView(LoginRequiredMixin, CreateView):
#     """Представление добавления доп. инфо по судну."""

#     model = VesselExtraInfo
#     template_name = "/applications/vessels/vesselextrainfo_create.html"
#     form_class = VesselExtraInfoCreateForm
#     login_url = "login"

#     def get_success_url(self):
#         company = get_object_or_404(Company, slug=self.kwargs["slug"])
#         return reverse_lazy(
#             "vesselextrainfo_detail", kwargs={"slug": company.slug}
#         )  # noqa: E501

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = "Добавление города"
#         context["company"] = get_object_or_404(
#             Company, slug=self.kwargs["slug"]
#         )  # noqa: E501
#         return context

#     def form_valid(self, form):
#         """Автосохранение поля company."""
#         instance = form.save(commit=False)
#         form.instance.created_by = self.request.user
#         form.instance.company = get_object_or_404(
#             Company, slug=self.kwargs["slug"]
#         )  # noqa: E501
#         instance.save()
#         return super().form_valid(form)


class VesselExtraInfoDetailView(DetailView):
    """Представление для вывода доп. инфо по судну и заявке."""

    model = VesselExtraInfo
    template_name = "applications/vessels/vesselextrainfo_detail.html"
    context_object_name = "vesselextrainfo"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Доп. инфо по судну и заявке"  # type: ignore # noqa: E501
        return context


class VesselExtraInfoUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, UpdateView
):  # noqa: E501
    """Представление обновления адреса."""

    model = VesselExtraInfo
    template_name = "applications/vessels/vesselextrainfo_update.html"
    context_object_name = "vesselextrainfo"
    form_class = VesselExtraInfoUpdateForm
    login_url = "login"
    success_message = "Доп. инфо по судну и заявке была успешно обновлена"

    def get_initial(self):
        user = self.request.user
        branch_number = user.office_number.number[0:3]  # type: ignore
        initial = {"branch_number": branch_number}
        return initial

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["title"] = "Обновление инфо по судну и заявке"
        return context

    def form_valid(self, form):
        form.instance.company = get_object_or_404(  # type: ignore
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        form.save()  # type: ignore
        return super().form_valid(form)


# class EmployeeSearchResultView(ListView):
#     """Реализация поиска работника на сайте."""

#     model = Employee
#     context_object_name = "employees"
#     paginate_by = 10
#     allow_empty = True
#     template_name = "companies/employees/employee_search_result.html"

#     def get_queryset(self):
#         query = self.request.GET.get("do")
#         search_vector = SearchVector(
#             "first_name", weight="B"
#         ) + SearchVector(  # noqa: E501
#             "second_name", weight="A"
#         )
#         search_query = SearchQuery(query)  # type: ignore
#         return (
#             self.model.objects.annotate(rank=SearchRank(search_vector, search_query))  # type: ignore # noqa: E501
#             .filter(rank__gte=0.3)
#             .order_by("-rank")
#         )

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = f'Результаты поиска: {self.request.GET.get("do")}'
#         return context

# =================== функционал Document ===================


class FormCreateView(LoginRequiredMixin, CreateView):
    """Представление добавления судна."""

    model = Form
    template_name = "applications/documents/form_create.html"
    form_class = FormCreateForm
    login_url = "login"

    def get_success_url(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        application = get_object_or_404(Application, pk=self.kwargs["pk"])
        return reverse_lazy(
            "document_create",
            kwargs={"slug": company.slug, "pk": application.pk},  # noqa: E501
        )  # noqa: E501

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить форму документа"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["application"] = get_object_or_404(
            Application, pk=self.kwargs["pk"]
        )  # noqa: E501
        return context

    def form_valid(self, form):
        """Автосохранение поля form."""
        instance = form.save(commit=False)
        form.instance.created_by = self.request.user
        # form.instance.company = get_object_or_404(
        #     Company, slug=self.kwargs["slug"]
        # )  # noqa: E501
        instance.save()
        return super().form_valid(form)


class FormAutocomplete(autocomplete.Select2QuerySetView):
    """Автозаполнение для поля суда."""

    def get_queryset(self):
        qs = Form.objects.all()
        if self.q:
            qs = qs.filter(number__istartswith=self.q)
        return qs


class DocumentListView(LoginRequiredMixin, ListView):
    """Представления для вывода списка выданных документов по заявке."""

    model = Document
    template_name = "applications/documents/document_list.html"
    login_url = "login"
    context_object_name = "documents"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        application = get_object_or_404(Application, pk=self.kwargs["pk"])  # noqa: E501
        return queryset.filter(application=application)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Перечень выданных документов"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["application"] = get_object_or_404(
            Application, pk=self.kwargs["pk"]
        )  # noqa: E501
        return context


class DocumentDetailView(DetailView):
    """Представление для вывода отдельного документа."""

    model = Document
    template_name = "applications/documents/document_detail.html"
    context_object_name = "document"
    slug_url_kwarg = "pk"
    pk_url_kwarg = "id"

    # slug_field = 'isbn'
    # slug_url_kwarg = 'isbn'
    # def get_queryset(self):
    # if self.request.user.is_authenticated:
    # return Book.objects.filter(is_published=True, user=self.request.user)
    # else:
    # return Book.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Документ № {self.object}"  # type: ignore # noqa: E501
        return context


class DocumentCreateView(LoginRequiredMixin, CreateView):
    """Представление добавления документа или письма об одобрении."""

    model = Document
    template_name = "applications/documents/document_create.html"
    form_class = DocumentCreateForm
    login_url = "login"

    def get_success_url(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        application = get_object_or_404(Application, pk=self.kwargs["pk"])
        return reverse_lazy(
            "document_list",
            kwargs={"slug": company.slug, "pk": application.pk},  # noqa: E501
        )  # noqa: E501

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить документ"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["application"] = get_object_or_404(
            Application, pk=self.kwargs["pk"]
        )  # noqa: E501
        return context

    def form_valid(self, form):
        """Автосохранение поля company."""
        instance = form.save(commit=False)
        form.instance.created_by = self.request.user
        form.instance.application = get_object_or_404(
            Application, pk=self.kwargs["pk"]
        )  # noqa: E501
        instance.save()
        return super().form_valid(form)


class DocumentUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, UpdateView
):  # noqa: E501
    """Представление обновления документа."""

    model = Document
    slug_url_kwarg = "pk"
    pk_url_kwarg = "id"
    template_name = "applications/documents/document_update.html"
    context_object_name = "document"
    form_class = DocumentUpdateForm
    login_url = "login"
    success_message = "Информация по документу была успешна обновлена"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["application"] = get_object_or_404(
            Application, pk=self.kwargs["pk"]
        )  # noqa: E501
        context["title"] = "Обновление данных документа"
        return context

    def form_valid(self, form):
        form.instance.application = get_object_or_404(  # type: ignore
            Application, pk=self.kwargs["pk"]
        )  # noqa: E501
        form.save()  # type: ignore
        return super().form_valid(form)


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    """Представление удаления счёта в банке."""

    model = Document
    slug_url_kwarg = "pk"
    pk_url_kwarg = "id"
    login_url = "login"
    context_object_name = "document"
    template_name = "applications/documents/document_delete.html"

    def get_success_url(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        application = get_object_or_404(Application, pk=self.kwargs["pk"])
        return reverse_lazy(
            "document_list",
            kwargs={"slug": company.slug, "pk": application.pk},  # noqa: E501
        )  # noqa: E501

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удалить документ №: {self.object}"   # type: ignore # noqa: E501
        return context


# =================== функционал Account ===================


class AccountDetailView(DetailView):
    """Представление для вывода стоимости услуги."""

    model = Account
    template_name = "applications/accounts/account_detail.html"
    context_object_name = "account"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Стоимость услуги"  # type: ignore # noqa: E501
        return context


class AccountUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, UpdateView
):  # noqa: E501
    """Представление редактирования стоимости услуги."""

    model = Account
    template_name = "applications/accounts/account_update.html"
    context_object_name = "account"
    form_class = AccountUpdateForm
    login_url = "login"
    success_message = "Стоимость услуги была успешно обновлена"

    # def get_initial(self):
    #     user = self.request.user
    #     branch_number = user.office_number.number[0:3]  # type: ignore
    #     initial = {"branch_number": branch_number}
    #     return initial

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["title"] = "Обновить расчёт стоимости"
        return context

    def form_valid(self, form):
        form.instance.company = get_object_or_404(  # type: ignore
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        form.save()  # type: ignore
        return super().form_valid(form)


# -------- Функционал вывода на печать документов --------

def get_docx_template(survey_code, report_type):
    """Получить определённый шаблон docx в зависимости
       от кода услуги."""
    # report_type is certificate on AGREEMENT-application or
    # ACCEPTANCE of delivery service report
    match survey_code:
        case "00001" | "00003" | "00011":
            if report_type == "agreement":
                return "810_1_1.docx"
            return "430_3_4.docx"
        case "00006":
            if report_type == "agreement":
                return "810_1_11.docx"
            return "430_3_1.docx"
        case "00101":
            if report_type == "agreement":
                return "810_1_2_w.docx"
            return "430_3_1.docx"
        case _:
            return "404_page.docx"


def get_genitive_case(phrase):
    """Функция перевода слов в родительный падеж."""
    # whole sentence with removing conjunctions, prepositions and punctuation
    # import pymorphy3
    # import string
    # text = "первое число месяца, дня и года".translate(str.maketrans('', '', string.punctuation)) # noqa: E501
    # morph = pymorphy3.MorphAnalyzer()
    # words = text.split()
    # conjunctions = [word for word in words if morph.parse(word)[0].tag.POS == 'CONJ'] # noqa: E501
    # sentence = [word for word in words if word not in conjunctions]
    # st = (' '.join(sentence))
    # status = ' '.join(morph.parse(word)[0].inflect({'gent'}).word for word in st.split()) # noqa: E501
    # print(status)

    # with one word
    # morph = pymorphy3.MorphAnalyzer()
    # theword = morph.parse(phrase)[0]
    # gent = theword.inflect({'gent'})  # type: ignore
    # return gent.word  # type: ignore

    # parse a phrase with several words without punctuation, conj and prepos
    morph = pymorphy3.MorphAnalyzer()
    result = ' '.join(morph.parse(word)[0].inflect({'gent'}).word for word in phrase.split())  # type: ignore # noqa: E501
    return result


def get_genitive_case_lastname(lastname):
    """Функция перевода фамилий в родительный падеж."""
    # -------------------------------------------------------
    # Исправление бага с фамилией для питона 3+
    # https://github.com/damirazo/Petrovich/issues/8
    # в petrovich -> main.py
    # with open(rules_path, 'r') as fp:
    #     self.data = json.load(fp)
    # Заменяем их на эти:
    # try:
    #     with open(rules_path, 'r', encoding='utf8') as fp:
    #         self.data = json.load(fp)
    # except:
    #     with open(rules_path, 'r') as fp:
    #         self.data = json.load(fp)
    # в lastname заменить str на None в значении по умолчанию
    # -------------------------------------------------------
    p = Petrovich()
    cased_lname = p.lastname(lastname, Case.GENITIVE)
    return cased_lname


def get_genitive_case_proxy(proxy, number=None, date=None):
    """Функция перевода названий документов,
       на основании которых действует заявитель,
       в родительный падеж."""
    # power_of_attoney_gen = ""
    match proxy:
        case "Устав":
            power_of_attoney_gen = "Устава"
        case "Кодекс торгового мореплавания (КТМ РФ)":
            power_of_attoney_gen = "Кодекса торгового мореплавания (КТМ РФ)"
        case "Доверенность":
            power_of_attoney_gen = f"Доверенности № {number} от {date.strftime("%d.%m.%Y")}"  # type: ignore # noqa: E501
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


def is_vessel_None(name=None, rs=None, imo=None):
    """Проверка судна на None для заявок в промышленности."""
    if name is not None:
        vessel_attribute = f'"{name.name}"'
    elif rs is not None:
        vessel_attribute = is_none(rs.rs_number)
    elif imo is not None:
        vessel_attribute = is_none(imo.imo_number)
    else:
        vessel_attribute = ""
    return vessel_attribute


def is_legal_address_same(is_same_check, postal_address, legal_address=None):
    """Проверка на совпадение почтового и юридического адресов."""
    if is_same_check is True:
        return postal_address
    return legal_address


def get_issued_docs(document_qs=None, survey_code="00001", document_date=None):
    """Выданные документы в зависимости от кода услуги."""
    if document_qs is None:
        return ""
    match survey_code:
        case "00001" | "00003" | "00011":
            if document_date is None:
                documents = f"{document_qs.first().form} № {document_qs.first()}"  # noqa: E501
            else:
                documents = f"{document_qs.first().form} № {document_qs.first()} от {document_date.strftime("%d.%m.%Y")}"  # type: ignore # noqa: E501
        case "00006":
            if document_date is None:
                documents = f"{document_qs.first().form} {document_qs.first()}"  # noqa: E501
            else:
                documents = f"{document_qs.first().form} {document_qs.first()} от {document_date.strftime("%d.%m.%Y")}"  # type: ignore # noqa: E501
        # add logic for several issued docums and then to merge with 00001
        case "00101":
            if document_date is None:
                documents = f"{document_qs.first().form} № {document_qs.first()}"  # noqa: E501
            else:
                documents = f"{document_qs.first().form} № {document_qs.first()} от {document_date.strftime("%d.%m.%Y")}"  # type: ignore # noqa: E501
        case _:
            return "404_page.docx"
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
    docx_template = get_docx_template(application.survey_code, button_name)
    doc = DocxTemplate(f"templates/docx/{docx_template}")

    context = {
        # for agreement-applications
        "application": application.number,
        "day": application.date.strftime("%d"),  # type: ignore
        "month": dateformat.format(application.date, settings.DATE_FORMAT),
        "year": application.date.strftime("%y"),  # type: ignore
        "vessel": is_vessel_None(application.vessel, None, None),  # type: ignore # noqa: E501
        "rs_number": is_vessel_None(None, application.vessel, None),  # type: ignore # noqa: E501
        "imo_number": is_vessel_None(None, None, application.vessel),  # type: ignore # noqa: E501
        "survey_scope": application,
        "survey_object": application.get_survey_object_display(),  # type: ignore # noqa: E501
        "city": application.city,
        "date": application.date.strftime("%d.%m.%Y"),
        "company": company,
        "applicant": f"{get_genitive_case(application.applicant_signer.position)} {get_genitive_case_lastname(application.applicant_signer.second_name)} {application.applicant_signer.first_name[0]}. {application.applicant_signer.patronymic_name[0]}.",  # type: ignore # noqa: E501
        "applicant_proxy": get_genitive_case_proxy(application.applicant_signer.get_proxy_type_display(), application.applicant_signer.proxy_number, application.applicant_signer.proxy_date),  # type: ignore # noqa: E501
        "authorized_person": f"{application.authorized_person}, {application.authorized_person.phone_number}, {application.authorized_person.email}",  # type: ignore # noqa: E501
        "previous_survey_place": application.vesselextrainfo.city,  # type: ignore # noqa: E501
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
        # for reports on acceptance-delivery services
        "surveyor": f"{request.user.position} {request.user.last_name} {request.user.first_name[0]}. {request.user.patronymic_name[0]}.",  # noqa: E501
        "surveyor_proxy": f"Доверенности № {request.user.proxy_number} от {request.user.proxy_date.strftime("%d.%m.%Y")}",  # type: ignore # noqa: E501
        "applicant_nominative": f"{application.applicant_signer.position} {application.applicant_signer.second_name} {application.applicant_signer.first_name[0]}. {application.applicant_signer.patronymic_name[0]}.",  # type: ignore # noqa: E501
        "issued_docs": get_issued_docs(application.documents, application.survey_code, application.completion_date),  # type: ignore # noqa: E501
        "service_cost": get_sum_in_words(application.account.service_cost, company.bank_accounts.filter(current_bankaccount=True).first().account_currency),  # type: ignore # noqa: E501
        "tax": get_sum_in_words(application.account.service_cost, company.bank_accounts.filter(current_bankaccount=True).first().account_currency, "vat"),  # type: ignore # noqa: E501
        "total": get_sum_in_words(application.account.service_cost, company.bank_accounts.filter(current_bankaccount=True).first().account_currency, "total"),  # type: ignore # noqa: E501
        "surveyor_signer": f"{request.user.first_name[0]}. {request.user.patronymic_name[0]}. {request.user.last_name}",  # type: ignore # noqa: E501
    }  # noqa: E501

    doc.render(context)
    doc.save(f"templates/docx/saved/{docx_template}")

    doc_io = io.BytesIO()  # create a file-like object
    doc.save(doc_io)  # save data to file-like object
    doc_io.seek(0)  # go to the beginning of the file-like object

    response = HttpResponse(doc_io.read())

    # Content-Disposition header makes a file downloadable
    response["Content-Disposition"] = (
        # "attachment; filename=810_1_1.docx"  # noqa: E501
        f"attachment; filename={docx_template}"  # noqa: E501
    )

    # Set the appropriate Content-Type for docx file
    response["Content-Type"] = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # noqa: E501
    )
    return response

# --- конец функционала вывода на печать документов ---
