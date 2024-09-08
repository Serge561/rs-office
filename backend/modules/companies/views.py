# pylint: disable=no-member, too-many-ancestors, unused-argument, relative-beyond-top-level, line-too-long # noqa: E501
"""Представления для модели companies."""
# from django.http import JsonResponse
from dal import autocomplete
from django.shortcuts import get_object_or_404  # , redirect, render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin  # noqa: E501
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
)  # noqa: E501
from django.urls import reverse_lazy
from django.db.models import Q

# from localflavor.ru.ru_regions import RU_REGIONS_CHOICES
from .models import (
    Address,
    Bank,
    BankAccount,
    City,
    Company,
    Employee,
    RussianRegions,
)  # noqa: E501
from ..services.mixins import AdminRequiredMixin, RSUserOnlyMixin
from .forms import (
    AddressCreateForm,
    AddressUpdateForm,
    BankAccountCreateForm,
    BankAccountUpdateForm,
    BankCreateForm,
    CityCreateForm,
    CompanyCreateForm,
    CompanyUpdateForm,
    EmployeeCreateForm,
    EmployeeUpdateForm,
)


class CompanyListView(LoginRequiredMixin, ListView):
    """Представления для вывода списка компаний на главной странице."""

    model = Company
    template_name = "companies/company_list.html"
    login_url = "login"
    context_object_name = "companies"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:  # type: ignore
            return queryset
        user_office_id = user.office_number.id  # type: ignore
        return queryset.filter(responsible_offices=user_office_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Главная страница"
        return context


class CompanyDetailView(LoginRequiredMixin, DetailView):
    """Представление для вывода карточки компании."""

    model = Company
    template_name = "companies/company_detail.html"
    context_object_name = "company"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.name  # type: ignore
        return context


class CompanyCreateView(RSUserOnlyMixin, CreateView):
    """Представление создания карточки компании на сайте."""

    model = Company
    template_name = "companies/company_create.html"
    form_class = CompanyCreateForm
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавить карточку компании"
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.save()
        return super().form_valid(form)


class CompanyUpdateView(RSUserOnlyMixin, SuccessMessageMixin, UpdateView):
    """Представление обновления карточки на сайте."""

    model = Company
    template_name = "companies/company_update.html"
    context_object_name = "company"
    form_class = CompanyUpdateForm
    login_url = "login"
    success_message = "Карточка была успешно обновлена"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Обновление карточки: {self.object.name}"  # type: ignore # noqa: E501
        return context

    def form_valid(self, form):
        form.instance.updated_by = self.request.user  # type: ignore
        form.save()  # type: ignore
        return super().form_valid(form)


class CompanyDeleteView(AdminRequiredMixin, DeleteView):
    """Представление удаления карточки компании."""

    model = Company
    login_url = "login"
    success_url = reverse_lazy("home")
    context_object_name = "company"
    template_name = "companies/company_delete.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удаление карточки предприятия: {self.object.name}"  # type: ignore # noqa: E501
        return context


class CompanySearchResultView(LoginRequiredMixin, ListView):
    """Реализация поиска фирм на сайте."""

    model = Company
    context_object_name = "companies"
    paginate_by = 10
    allow_empty = True
    template_name = "companies/company_list.html"
    login_url = "login"

    def get_queryset(self):
        query = self.request.GET.get("do")
        search_vector = SearchVector(
            "extra_info", weight="B"
        ) + SearchVector(  # noqa: E501
            "name", weight="A"
        )
        search_query = SearchQuery(query)  # type: ignore
        return (
            self.model.objects.annotate(rank=SearchRank(search_vector, search_query))  # type: ignore # noqa: E501
            .filter(rank__gte=0.3)
            .order_by("-rank")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f'Результаты поиска: {self.request.GET.get("do")}'
        return context


# ======================== Функционал address ==============================


class CityAutocomplete(autocomplete.Select2QuerySetView):
    """Автозаполнение для поля города."""

    def get_queryset(self):
        qs = City.objects.all()
        if self.q:
            qs = qs.filter(  # type: ignore
                Q(name__istartswith=self.q) | Q(name_en__icontains=self.q)
            )  # noqa: E501
        return qs


class AddressListView(LoginRequiredMixin, ListView):
    """Представления для вывода списка адресов компании."""

    model = Address
    template_name = "companies/addresses/address_list.html"
    login_url = "login"
    context_object_name = "addresses"

    def get_queryset(self):
        queryset = super().get_queryset()
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return queryset.filter(company=company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Адреса предприятия"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        return context


class AddressCreateView(RSUserOnlyMixin, CreateView):
    """Представление добавления адреса компании."""

    model = Address
    template_name = "companies/addresses/address_create.html"
    form_class = AddressCreateForm
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавление адреса компании"
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


class AddressUpdateView(RSUserOnlyMixin, SuccessMessageMixin, UpdateView):
    """Представление обновления адреса."""

    model = Address
    template_name = "companies/addresses/address_update.html"
    context_object_name = "address"
    form_class = AddressUpdateForm
    login_url = "login"
    success_message = "Адрес был успешно обновлен"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["title"] = "Обновление адреса компании"
        return context

    def form_valid(self, form):
        form.instance.updated_by = self.request.user  # type: ignore
        form.instance.company = get_object_or_404(  # type: ignore
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        form.save()  # type: ignore
        return super().form_valid(form)


class AddressDeleteView(RSUserOnlyMixin, DeleteView):
    """Представление удаления адреса компании."""

    model = Address
    login_url = "login"
    context_object_name = "address"
    template_name = "companies/addresses/address_delete.html"

    def get_success_url(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return reverse_lazy(
            "company_address_list", kwargs={"slug": company.slug}
        )  # noqa: E501

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удаление адреса предприятия: {self.object.address_type}"  # type: ignore # noqa: E501
        return context


class CountryAutocomplete(autocomplete.Select2ListView):
    """Автозаполнение для поля города."""

    def get_list(self):
        country_list = City.COUNTRIES
        return country_list


class CountryEnAutocomplete(autocomplete.Select2ListView):
    """Автозаполнение для поля города."""

    def get_list(self):
        country_list_en = City.COUNTRIES_EN
        return country_list_en


class RegionAutocomplete(autocomplete.Select2ListView):
    """Автозаполнение для поля область или край РФ."""

    def get_list(self):
        # ru_region_list = RU_REGIONS_CHOICES
        ru_region_list = RussianRegions.choices
        return ru_region_list


class CityCreateView(RSUserOnlyMixin, CreateView):
    """Представление добавления города."""

    model = City
    template_name = "companies/addresses/city_create.html"
    form_class = CityCreateForm
    login_url = "login"

    def get_success_url(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return reverse_lazy(
            "address_create", kwargs={"slug": company.slug}
        )  # noqa: E501

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавление города"
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


# ======================== Функционал bank ==============================


class BankAutocomplete(autocomplete.Select2QuerySetView):
    """Автозаполнение для поля банки."""

    def get_queryset(self):
        qs = Bank.objects.all()
        if self.q:
            # qs = qs.filter(name__istartswith=self.q)
            qs = qs.filter(name__icontains=self.q)
        return qs


class BankAccountListView(LoginRequiredMixin, ListView):
    """Представления для вывода списка реквизитов счётов компании."""

    model = BankAccount
    template_name = "companies/bank_accounts/bank_account_list.html"
    login_url = "login"
    context_object_name = "bank_accounts"

    def get_queryset(self):
        queryset = super().get_queryset()
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return queryset.filter(company=company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Банковские реквизиты счетов компании"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        return context


class BankAccountCreateView(RSUserOnlyMixin, CreateView):
    """Представление добавления расчётного счёта компании."""

    model = Bank
    template_name = "companies/bank_accounts/bank_account_create.html"
    form_class = BankAccountCreateForm
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавление расчётного счёта компании"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        return context

    def form_valid(self, form):
        """Автосохранение поля company."""
        instance = form.save(commit=False)
        # form.instance.created_by = self.request.user
        form.instance.company = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        instance.save()
        return super().form_valid(form)


class BankAccountUpdateView(
    RSUserOnlyMixin, SuccessMessageMixin, UpdateView
):  # noqa: E501
    """Представление обновления расчётного счёта."""

    model = BankAccount
    template_name = "companies/bank_accounts/bank_account_update.html"
    context_object_name = "bankaccount"
    form_class = BankAccountUpdateForm
    login_url = "login"
    success_message = "Расчётный счёт был успешно обновлен"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["title"] = "Обновление расчётного счёта компании"
        return context

    def form_valid(self, form):
        form.instance.updated_by = self.request.user  # type: ignore
        form.instance.company = get_object_or_404(  # type: ignore
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        form.save()  # type: ignore
        return super().form_valid(form)


class BankAccountDeleteView(RSUserOnlyMixin, DeleteView):
    """Представление удаления счёта в банке."""

    model = BankAccount
    login_url = "login"
    context_object_name = "bankaccount"
    template_name = "companies/bank_accounts/bank_account_delete.html"

    def get_success_url(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return reverse_lazy(
            "company_bankaccount_list", kwargs={"slug": company.slug}
        )  # noqa: E501

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удаление расчётного счёта компании: {self.object.account_currency}"  # type: ignore # noqa: E501
        return context


class BankDetailView(LoginRequiredMixin, DetailView):
    """Представление для вывода реквизитов банка."""

    model = Bank
    template_name = "companies/bank_accounts/bank_detail.html"
    login_url = "login"
    context_object_name = "bank"
    slug_url_kwarg = "pk"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f'Реквизиты банка "{self.object}"'  # type: ignore # noqa: E501
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["account"] = get_object_or_404(
            BankAccount, pk=self.kwargs["pk"]
        )  # noqa: E501
        return context


class BankCreateView(RSUserOnlyMixin, CreateView):
    """Представление добавления банка."""

    model = Bank
    template_name = "companies/bank_accounts/bank_create.html"
    form_class = BankCreateForm
    login_url = "login"

    def get_success_url(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return reverse_lazy(
            "bank_account_create", kwargs={"slug": company.slug}
        )  # noqa: E501

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавление банка"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        return context

    def form_valid(self, form):
        """Автосохранение поля bank."""
        instance = form.save(commit=False)
        form.instance.created_by = self.request.user
        form.instance.company = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        instance.save()
        return super().form_valid(form)


# ======================== Функционал employee ==============================


class EmployeeListView(LoginRequiredMixin, ListView):
    """Представления для вывода списка работников компании."""

    model = Employee
    template_name = "companies/employees/employee_list.html"
    login_url = "login"
    context_object_name = "employees"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return queryset.filter(company=company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Список работников компании"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """Представление для вывода профиля работника компании."""

    model = Employee
    template_name = "companies/employees/employee_detail.html"
    login_url = "login"
    context_object_name = "employee"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object  # type: ignore
        return context


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    """Представление добавления профиля работника компании."""

    model = Employee
    template_name = "companies/employees/employee_create.html"
    form_class = EmployeeCreateForm
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Добавление профиля работника компании"
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        return context

    def form_valid(self, form):
        """Автосохранение поля employee."""
        instance = form.save(commit=False)
        form.instance.created_by = self.request.user
        form.instance.company = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        instance.save()
        return super().form_valid(form)


class EmployeeUpdateView(
    LoginRequiredMixin, SuccessMessageMixin, UpdateView
):  # noqa: E501
    """Представление обновления профиля работника компании."""

    model = Employee
    template_name = "companies/employees/employee_update.html"
    context_object_name = "employee"
    form_class = EmployeeUpdateForm
    login_url = "login"
    success_message = "Профиль работника компании был успешно обновлен"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["title"] = "Обновление профиля работника компании"
        return context

    def form_valid(self, form):
        form.instance.updated_by = self.request.user  # type: ignore
        form.instance.company = get_object_or_404(  # type: ignore
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        form.save()  # type: ignore
        return super().form_valid(form)


class EmployeeSearchResultView(LoginRequiredMixin, ListView):
    """Реализация поиска работника на сайте."""

    model = Employee
    context_object_name = "employees"
    paginate_by = 10
    allow_empty = True
    template_name = "companies/employees/employee_search_result.html"
    login_url = "login"

    def get_queryset(self):
        query = self.request.GET.get("do")
        search_vector = SearchVector(
            "first_name", weight="B"
        ) + SearchVector(  # noqa: E501
            "second_name", weight="A"
        )
        search_query = SearchQuery(query)  # type: ignore
        return (
            self.model.objects.annotate(rank=SearchRank(search_vector, search_query))  # type: ignore # noqa: E501
            .filter(rank__gte=0.3)
            .order_by("-rank")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f'Результаты поиска: {self.request.GET.get("do")}'
        return context


class StaffSearchResultView(LoginRequiredMixin, ListView):
    """Реализация поиска служащего определённой компании."""

    model = Employee
    context_object_name = "employees"
    allow_empty = True
    template_name = "companies/employees/employee_list.html"
    login_url = "login"

    def get_queryset(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        query = self.request.GET.get("do")
        search_vector = SearchVector(
            "first_name", weight="B"
        ) + SearchVector(  # noqa: E501
            "second_name", weight="A"
        )
        search_query = SearchQuery(query)  # type: ignore
        return (
            self.model.objects.annotate(rank=SearchRank(search_vector, search_query))  # type: ignore # noqa: E501
            .filter(rank__gte=0.3)
            .filter(company=company)
            .order_by("-rank")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = get_object_or_404(
            Company, slug=self.kwargs["slug"]
        )  # noqa: E501
        context["title"] = f'Результаты поиска: {self.request.GET.get("do")}'
        return context


class EmployeeDeleteView(AdminRequiredMixin, DeleteView):
    """Представление удаления работника компании."""

    model = Employee
    login_url = "login"
    context_object_name = "employee"
    template_name = "companies/employees/employee_delete.html"

    def get_success_url(self):
        company = get_object_or_404(Company, slug=self.kwargs["slug"])
        return reverse_lazy(
            "company_employee_list", kwargs={"slug": company.slug}
        )  # noqa: E501

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Удаление работника компании: {self.object}"  # type: ignore # noqa: E501
        return context
