"""Админ-панель модели компаний."""

from django.contrib import admin
from .models import Company, City, Address, Bank, BankAccount, Employee

admin.site.site_header = 'Панель управления сайта "Офис РС"'


# @admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    """Админ-панель компаний."""

    model = Company
    readonly_fields = (
        "id",
        "slug",
    )
    list_display = [
        "id",
        "name",
        "extra_info",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    list_filter = ["responsible_offices"]
    search_fields = ("name",)
    list_display_links = (
        "id",
        "name",
    )
    autocomplete_fields = ["responsible_offices"]
    list_select_related = ["created_by"]


class CityAdmin(admin.ModelAdmin):
    """Админ-панель городов."""

    model = City
    list_display = [
        "id",
        "name",
        "district",
        "country",
        "region",
        "created_by",
        "created_at",
    ]
    list_filter = ["country", "region"]
    readonly_fields = ("id",)
    search_fields = ("name",)
    list_display_links = (
        "id",
        "name",
    )
    list_select_related = ["created_by"]


class AddressAdmin(admin.ModelAdmin):
    """Админ-панель компаний."""

    # form = MyArticleAdminForm
    model = Address
    list_display = [
        "id",
        "company",
        "city",
        # "postal_code",
        # "address_line",
        "address_type",
        "is_same",
    ]  # noqa: E501
    readonly_fields = ("id",)
    list_filter = ["city"]
    # search_fields = ("company",)
    list_display_links = (
        "id",
        "company",
        # "address_line",
    )
    autocomplete_fields = ["company", "city"]
    list_select_related = ["company", "city", "updated_by"]


class BankAdmin(admin.ModelAdmin):
    """Админ-панель банков."""

    # form = MyArticleAdminForm
    model = Bank
    list_display = [
        "id",
        "name",
        "bic",
        "correspondent_account",
        "regional_treasury_account",
        # "created_at",
        # "updated_at",
        # "created_by",
        # "updated_by",
    ]  # noqa: E501
    readonly_fields = ("id",)
    search_fields = ("name",)
    list_display_links = (
        "id",
        "name",
    )
    list_select_related = ["created_by"]


class BankAccountAdmin(admin.ModelAdmin):
    """Админ-панель реквизитов расчётных счетов компаний."""

    model = BankAccount
    list_display = [
        "id",
        "company",
        "bank",
        "bank_account",
        "account_currency",
    ]  # noqa: E501
    readonly_fields = ("id",)
    # search_fields = ("company",)
    list_filter = ["bank", "account_currency"]
    list_display_links = (
        "id",
        "bank_account",
    )
    autocomplete_fields = ["company", "bank"]
    list_select_related = ["company", "bank"]


class EmployeeAdmin(admin.ModelAdmin):
    """Админ-панель работников компаний."""

    model = Employee
    list_display = [
        "id",
        "company",
        "second_name",
        "first_name",
        "patronymic_name",
        "phone_number",
        "extra_number",
        "is_quit",
        "extra_info",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]  # noqa: E501
    readonly_fields = ("id",)
    list_filter = ["company"]
    search_fields = ("second_name",)
    list_display_links = (
        "id",
        "company",
        "second_name",
    )
    autocomplete_fields = ["company"]
    list_select_related = ["company", "created_by", "updated_by"]


admin.site.register(Company, CompanyAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Bank, BankAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Employee, EmployeeAdmin)
