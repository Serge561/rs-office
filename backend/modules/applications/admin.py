"""Админ-панель модели заявок."""

from django.contrib import admin
from .models import (
    Application,
    Vessel,
    VesselExtraInfo,
    Form,
    Document,
    Account,
)  # noqa: E501


class ApplicationAdmin(admin.ModelAdmin):
    """Админ-панель заявок."""

    model = Application
    list_display = [
        "id",
        "company",
        "number",
        "date",
        "completion_date",
        "survey_code",
        "survey_type",
        "survey_scope",
        "vessel",
    ]
    list_filter = ["company", "vessel"]
    readonly_fields = ("id",)
    search_fields = ("number", "company", "vessel")
    list_display_links = (
        "id",
        "company",
        "number",
        "vessel",
    )
    autocomplete_fields = [
        "city",
        "company",
        "vessel",
        "applicant_signer",
        "authorized_person",
    ]
    list_prefetch_related = ["assigned_surveyors"]
    list_select_related = [
        "city",
        "company",
        "vessel",
        "register_signer",
        "applicant_signer",
        "authorized_person",
        "created_by",
        "updated_by",
    ]


class VesselAdmin(admin.ModelAdmin):
    """Админ-панель судов."""

    model = Vessel
    list_display = [
        "id",
        "name",
        "rs_number",
        "imo_number",
        "flag",
        "vessel_stat_group",
        "created_by",
        "updated_by",
    ]
    list_filter = ["flag", "vessel_stat_group"]
    readonly_fields = ("id",)
    search_fields = ("name", "rs_number", "imo_number")
    list_display_links = (
        "id",
        "name",
        "rs_number",
    )
    list_select_related = ["created_by", "updated_by"]


class VesselExtraInfoAdmin(admin.ModelAdmin):
    """Админ-панель доп. инфо по судам."""

    model = VesselExtraInfo
    list_display = [
        "application",
        "class_status",
        "due_date",
        "completion_expected_date",
    ]
    search_fields = ("application",)
    list_display_links = (
        # "id",
        "application",
    )
    autocomplete_fields = [
        "city",
        "application",
    ]
    list_select_related = ["city", "application"]
    list_prefetch_related = ["assigned_surveyors"]


class FormAdmin(admin.ModelAdmin):
    """Админ-панель форм документов."""

    model = Form
    list_display = [
        "id",
        "number",
        "form_type",
        "description",
    ]
    list_filter = ["form_type", "number"]
    readonly_fields = ("id",)
    search_fields = ("number",)
    list_display_links = (
        "id",
        "number",
    )
    list_select_related = ["created_by", "updated_by"]


class DocumentAdmin(admin.ModelAdmin):
    """Админ-панель выданных документов."""

    model = Document
    list_display = [
        "id",
        "application",
        "number",
        "form",
        "item_particulars",
    ]
    readonly_fields = ("id",)
    search_fields = (
        "application",
        "number",
    )
    list_display_links = (
        "id",
        "application",
        "number",
    )
    list_select_related = ["form", "application"]


class AccountAdmin(admin.ModelAdmin):
    """Админ-панель стоимости услуги."""

    model = Account
    list_display = [
        "application",
        "service_cost",
        "extra_info",
    ]
    search_fields = ("application",)
    list_display_links = ("application",)
    autocomplete_fields = [
        "application",
    ]
    list_select_related = ["application"]


admin.site.register(Application, ApplicationAdmin)
admin.site.register(Vessel, VesselAdmin)
admin.site.register(VesselExtraInfo, VesselExtraInfoAdmin)
admin.site.register(Form, FormAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Account, AccountAdmin)
