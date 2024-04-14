# pylint: disable=line-too-long, unused-argument, too-many-ancestors, too-few-public-methods # noqa: E501
"""Представления для модели applications."""

import io
from dal import autocomplete
from docxtpl import DocxTemplate
from django.http import HttpResponse
from django.shortcuts import get_object_or_404  # , redirect, render
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

# from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    # DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.messages.views import SuccessMessageMixin


# from django.contrib.postgres.search import (
#     SearchVector,
#     SearchQuery,
#     SearchRank,
# )  # noqa: E501
# from django.urls import reverse_lazy
from .models import (
    Application,
    Company,
    Vessel,
    VesselExtraInfo,
    Form,
    Document,
    Account,
)


# from ..services.mixins import AdminRequiredMixin

from .forms import (
    ApplicationCreateForm,
    ApplicationUpdateForm,
    VesselCreateForm,
    # VesselExtraInfoCreateForm,
    VesselExtraInfoUpdateForm,
    FormCreateForm,
    DocumentCreateForm,
    DocumentUpdateForm,
    AccountUpdateForm,
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
        context["title"] = f"Заявка № {self.object} от {self.object.date:%d.%m.%Y}"  # type: ignore # noqa: E501
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
    """Представления для вывода списка работников компании."""

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


def print_docs(request, **kwargs):
    """Функция печати документов."""

    doc = DocxTemplate("templates/docx/810_1_1_template.docx")

    company = get_object_or_404(Company, slug=kwargs["slug"])
    application = get_object_or_404(Application, id=kwargs["pk"])

    context = {
        "company": company,
        "service_cost": application.account.service_cost,  # type: ignore
    }  # noqa: E501

    doc.render(context)
    doc.save("templates/docx/810_1_1.docx")

    doc_io = io.BytesIO()  # create a file-like object
    doc.save(doc_io)  # save data to file-like object
    doc_io.seek(0)  # go to the beginning of the file-like object

    response = HttpResponse(doc_io.read())

    # Content-Disposition header makes a file downloadable
    response["Content-Disposition"] = (
        "attachment; filename=810_1_1_printed.docx"  # noqa: E501
    )

    # Set the appropriate Content-Type for docx file
    response["Content-Type"] = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # noqa: E501
    )
    return response
