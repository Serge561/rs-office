"""Маршруты приложения companies."""

from django.urls import path
from django.urls import re_path as url


from .views import (
    BankAccountCreateView,
    BankAccountDeleteView,
    BankAccountListView,
    BankAccountUpdateView,
    BankAutocomplete,
    # BankDetailView,
    BankCreateView,
    CompanyListView,
    CompanyDetailView,
    CompanyCreateView,
    CompanyUpdateView,
    CompanyDeleteView,
    CompanySearchResultView,
    AddressListView,
    AddressCreateView,
    AddressUpdateView,
    AddressDeleteView,
    CityAutocomplete,
    CountryAutocomplete,
    EmployeeCreateView,
    EmployeeDetailView,
    EmployeeListView,
    EmployeeSearchResultView,
    EmployeeUpdateView,
    RegionAutocomplete,
    CityCreateView,
    StaffSearchResultView,
)

urlpatterns = [
    path("", CompanyListView.as_view(), name="home"),
    path(
        "companies/create/", CompanyCreateView.as_view(), name="company_create"
    ),  # noqa: E501
    path(
        "companies/<str:slug>/update/",
        CompanyUpdateView.as_view(),
        name="company_update",
    ),
    path(
        "companies/<str:slug>/delete/",
        CompanyDeleteView.as_view(),
        name="company_delete",
    ),
    path(
        "companies/<str:slug>/",
        CompanyDetailView.as_view(),
        name="company_detail",  # noqa: E501
    ),  # noqa: E501
    path("search/", CompanySearchResultView.as_view(), name="search"),
    # path("autosuggest/", autosuggest, name="autosuggest"),
    # ================== address =====================
    path(
        "companies/<str:slug>/addresses/",
        AddressListView.as_view(),
        name="company_address_list",
    ),
    path(
        "companies/<str:slug>/addresses/create/",
        AddressCreateView.as_view(),
        name="address_create",
    ),
    path(
        "companies/<str:slug>/addresses/<int:pk>/update/",
        AddressUpdateView.as_view(),
        name="address_update",
    ),
    path(
        "companies/<str:slug>/addresses/<int:pk>/delete/",
        AddressDeleteView.as_view(),
        name="address_delete",
    ),
    url(
        r"^city-autocomplete/$",
        CityAutocomplete.as_view(),
        name="city-autocomplete",
    ),
    url(
        r"^country-autocomplete/$",
        CountryAutocomplete.as_view(),
        name="country-autocomplete",
    ),
    url(
        r"^region-autocomplete/$",
        RegionAutocomplete.as_view(),
        name="region-autocomplete",
    ),
    url(
        r"^bank-autocomplete/$",
        BankAutocomplete.as_view(),
        name="bank-autocomplete",
    ),
    path(
        "companies/<str:slug>/addresses/create/city_create/",
        CityCreateView.as_view(),
        name="city_create",
    ),
    # ================ bankaccount =================
    path(
        "companies/<str:slug>/bankaccounts/",
        BankAccountListView.as_view(),
        name="company_bankaccount_list",
    ),
    path(
        "companies/<str:slug>/bankaccounts/create/",
        BankAccountCreateView.as_view(),
        name="bankaccount_create",
    ),
    path(
        "companies/<str:slug>/bankaccounts/<int:pk>/update/",
        BankAccountUpdateView.as_view(),
        name="bankaccount_update",
    ),
    path(
        "companies/<str:slug>/bankaccounts/<int:pk>/delete/",
        BankAccountDeleteView.as_view(),
        name="bankaccount_delete",
    ),
    # path(
    #     "companies/<str:slug>/bankaccounts/<int:pk>/bank_detail/<int:id>/",
    #     BankDetailView.as_view(),
    #     name="bank_detail",
    # ),
    path(
        "companies/<str:slug>/bankaccounts/create/bank_create/",
        BankCreateView.as_view(),
        name="bank_create",
    ),
    # =============== employee ==================
    path(
        "companies/<str:slug>/employees/",
        EmployeeListView.as_view(),
        name="company_employee_list",
    ),
    path(
        "companies/<str:slug>/employees/<int:pk>/",
        EmployeeDetailView.as_view(),
        name="employee_detail",  # noqa: E501
    ),  # noqa: E501
    path(
        "companies/<str:slug>/employees/create/",
        EmployeeCreateView.as_view(),
        name="employee_create",
    ),
    path(
        "companies/<str:slug>/employees/<int:pk>/update/",
        EmployeeUpdateView.as_view(),
        name="employee_update",
    ),
    # path(
    #     "companies/<str:slug>/employees/<int:pk>/delete/",
    #     BankAccountDeleteView.as_view(),
    #     name="bankaccount_delete",
    # ),
    path(
        "companies/<str:slug>/employees/employee_create/",
        EmployeeCreateView.as_view(),
        name="employee_create",
    ),
    path(
        "search_employee/",
        EmployeeSearchResultView.as_view(),
        name="search_employee",  # noqa: E501
    ),
    path(
        "companies/<str:slug>/employees/search_staff/",
        StaffSearchResultView.as_view(),
        name="search_staff",  # noqa: E501
    ),
]
