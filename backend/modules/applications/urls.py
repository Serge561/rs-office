# pylint: disable=line-too-long, import-error
"""Маршруты приложения application."""

from django.urls import path
from django.urls import re_path as url

from .views import (
    AccountDetailView,
    AccountUpdateView,
    ApplicationCreateView,
    ApplicationDetailView,
    ApplicationListView,
    ApplicationUpdateView,
    DocumentCreateView,
    DocumentDeleteView,
    DocumentDetailView,
    DocumentListView,
    DocumentUpdateView,
    FormAutocomplete,
    FormCreateView,
    VesselAutocomplete,
    VesselCreateView,
    VesselDetailView,
    VesselUpdateView,
    VesselExtraInfoDetailView,
    VesselExtraInfoUpdateView,
    VesselSearchResultView,
    DashboardView,
    CurrentApplicationsView,
    CurrentApplicationsSurveyorView,
    AnnualReportA1View,
    print_docs,
)

urlpatterns = [
    path(
        "companies/<str:slug>/applications/",
        ApplicationListView.as_view(),
        name="company_application_list",
    ),
    path(
        "companies/<str:slug>/applications/<int:pk>/",
        ApplicationDetailView.as_view(),
        name="application_detail",
    ),
    path(
        "companies/<str:slug>/applications/create/",
        ApplicationCreateView.as_view(),
        name="application_create",
    ),
    path(
        "companies/<str:slug>/applications/<int:pk>/update/",
        ApplicationUpdateView.as_view(),
        name="application_update",
    ),
    # path(
    #     "companies/<str:slug>/application/<int:pk>/delete/",
    #     ApplicationDeleteView.as_view(),
    #     name="application_delete",
    # ),
    url(
        r"^vessel-autocomplete/$",
        VesselAutocomplete.as_view(),
        name="vessel-autocomplete",
    ),
    path(
        "search_vessel/",
        VesselSearchResultView.as_view(),
        name="search_vessel",
    ),
    path(
        "companies/<str:slug>/applications/create/vessel_create/",
        VesselCreateView.as_view(),
        name="vessel_create",
    ),
    path(
        "vessel_detail/<int:pk>/",
        VesselDetailView.as_view(),
        name="vessel_detail",
    ),
    path(
        "vessel_update/<int:pk>/update/",
        VesselUpdateView.as_view(),
        name="vessel_update",
    ),
    path(
        "companies/<str:slug>/applications/<int:pk>/vesselextrainfo/",
        VesselExtraInfoDetailView.as_view(),
        name="vesselextrainfo_detail",
    ),
    path(
        "companies/<str:slug>/applications/<int:pk>/vesselextrainfo/update/",
        VesselExtraInfoUpdateView.as_view(),
        name="vesselextrainfo_update",
    ),
    # ================ document =================
    path(
        "companies/<str:slug>/applications/<int:pk>/documents/create/form_create/",  # noqa: E501
        FormCreateView.as_view(),
        name="form_create",
    ),
    url(
        r"^form-autocomplete/$",
        FormAutocomplete.as_view(),
        name="form-autocomplete",
    ),
    path(
        "companies/<str:slug>/applications/<int:pk>/documents/",
        DocumentListView.as_view(),
        name="document_list",
    ),
    path(
        "companies/<str:slug>/applications/<int:pk>/documents/<int:id>/",
        DocumentDetailView.as_view(),
        name="document_detail",
    ),
    path(
        "companies/<str:slug>/applications/<int:pk>/documents/create/",
        DocumentCreateView.as_view(),
        name="document_create",
    ),
    path(
        "companies/<str:slug>/applications/<int:pk>/documents/<int:id>/update/",  # noqa: E501
        DocumentUpdateView.as_view(),
        name="document_update",
    ),
    path(
        "companies/<str:slug>/applications/<int:pk>/documents/<int:id>/delete/",  # noqa: E501
        DocumentDeleteView.as_view(),
        name="document_delete",
    ),
    # ================ account =================
    path(
        "companies/<str:slug>/applications/<int:pk>/account/",
        AccountDetailView.as_view(),
        name="account_detail",
    ),
    path(
        "companies/<str:slug>/applications/<int:pk>/account/update/",
        AccountUpdateView.as_view(),
        name="account_update",
    ),
    # =============== print docx ===============
    path(
        "companies/<str:slug>/applications/<int:pk>/account/print/",
        print_docs,
        name="print_doc",
    ),
    # ================ reports ================
    path(
        "dashboard_report/",
        DashboardView.as_view(),
        name="dashboard_report",
    ),
    path(
        "dashboard_report/current_applications/",
        CurrentApplicationsView.as_view(),
        name="current_applications",
    ),
    path(
        "dashboard_report/current_applications_surveyor/",
        CurrentApplicationsSurveyorView.as_view(),
        name="current_applications_surveyor",
    ),
    path(
        "dashboard_report/annual_report_a1/",
        AnnualReportA1View.as_view(),
        name="annual_report_a1",
    ),
]
