# pylint: disable=too-few-public-methods, line-too-long, import-error
"""Формы приложения companies."""
# import gettext
from django import forms
from dal import autocomplete
from phonenumber_field.formfields import PhoneNumberField
from localflavor.ru.forms import RUPostalCodeField

from .models import Address, Bank, BankAccount, City, Company, Employee


class CompanyCreateForm(forms.ModelForm):
    """Форма добавления карточки предприятия на сайте."""

    phone_number = PhoneNumberField(
        region="RU",
        label="Телефонный номер",
        required=False,
    )

    class Meta:
        """Мета форма добавления карточки предприятия на сайте."""

        model = Company
        fields = (
            "name",
            "phone_number",
            "email",
            "inn",
            "kpp",
            "ogrn",
            "responsible_offices",
            "extra_info",
        )

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        self.fields["extra_info"].widget.attrs["rows"] = 2
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )


class CompanyUpdateForm(CompanyCreateForm):
    """
    Форма обновления карточки предприятия на сайте
    """

    class Meta:
        """Мета формы обновления."""

        model = Company
        fields = CompanyCreateForm.Meta.fields

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )
            self.fields["extra_info"].widget.attrs["rows"] = 2


class AddressCreateForm(forms.ModelForm):
    """Форма добавления адреса компании."""

    postal_code = RUPostalCodeField()

    class Meta:
        """Мета форма добавления адреса компании."""

        model = Address
        exclude = (
            "company",
            "updated_by",
        )
        widgets = {
            "city": autocomplete.ModelSelect2(url="city-autocomplete")  # noqa: E501
        }

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )
        self.fields["is_same"].widget.attrs.update(
            {
                "class": "",
                "autocomplete": "off",
            }
        )


class AddressUpdateForm(AddressCreateForm):
    """Форма обновления адреса предприятия."""

    class Meta:
        """Мета формы обновления адреса."""

        model = Address
        fields = (
            "postal_code",
            "city",
            "address_line",
            "is_same",
        )
        widgets = {
            "city": autocomplete.ModelSelect2(url="city-autocomplete")  # noqa: E501
        }

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )
            self.fields["is_same"].widget.attrs.update(
                {
                    "class": "",
                    "autocomplete": "off",
                }
            )


class CityCreateForm(forms.ModelForm):
    """Форма добавления города."""

    class Meta:
        """Мета форма добавления адреса компании."""

        model = City
        fields = (
            "name",
            "country",
            "region",
            "district",
        )
        widgets = {
            "country": autocomplete.ListSelect2(
                url="country-autocomplete"
            ),  # noqa: E501
            "region": autocomplete.ListSelect2(url="region-autocomplete"),  # noqa: E501
        }

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )


# ====================== banks =======================

# for BankAccountModelForm
# class MyForm(forms.Form):
#     iban = IBANFormField()
#     bic = BICFormField()
#     расчётный счёт = IBANFormField()


class BankAccountCreateForm(forms.ModelForm):
    """Форма добавления банковского счёта компании."""

    class Meta:
        """Мета форма добавления банковского счёта компании."""

        model = BankAccount
        exclude = (
            "company",
            "updated_by",
        )
        widgets = {
            "bank": autocomplete.ModelSelect2(url="bank-autocomplete")  # noqa: E501
        }

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )
            self.fields["current_bankaccount"].widget.attrs.update(
                {
                    "class": "",
                    "autocomplete": "off",
                }
            )


class BankAccountUpdateForm(BankAccountCreateForm):
    """Форма обновления банковского счёта предприятия."""

    class Meta:
        """Мета формы обновления банковского счёта."""

        model = BankAccount
        fields = (
            "bank",
            "bank_account",
            "account_currency",
            "current_bankaccount",
        )
        widgets = {
            "bank": autocomplete.ModelSelect2(url="bank-autocomplete")  # noqa: E501
        }

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )
            self.fields["current_bankaccount"].widget.attrs.update(
                {
                    "class": "",
                    "autocomplete": "off",
                }
            )


class BankCreateForm(forms.ModelForm):
    """Форма добавления банка."""

    class Meta:
        """Мета форма добавления банка."""

        model = Bank
        fields = (
            "name",
            "bic",
            "correspondent_account",
            "regional_treasury_account",
            "extra_info",
        )

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        self.fields["extra_info"].widget.attrs["rows"] = 2
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )


# ========================= employee ============================


class EmployeeCreateForm(forms.ModelForm):
    """Форма добавления профиля работника компании."""

    phone_number = PhoneNumberField(
        region="RU",
        label="Телефонный номер",
        required=False,
    )

    class Meta:
        """Мета форма добавления профиля работника компании."""

        model = Employee
        exclude = (
            "company",
            "created_by",
            "updated_by",
        )

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        self.fields["proxy_date"].widget.attrs.update(
            {
                "id": "datepicker",
            }
        )
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )


class EmployeeUpdateForm(EmployeeCreateForm):
    """Форма обновления профиля работника."""

    phone_number = PhoneNumberField(
        region="RU",
        label="Телефонный номер",
        required=False,
    )

    class Meta:
        """Мета формы обновления профиля работника."""

        model = Employee
        fields = (
            "second_name",
            "first_name",
            "patronymic_name",
            "position",
            "phone_number",
            "extra_number",
            "email",
            "proxy_type",
            "proxy_number",
            "proxy_date",
            "extra_info",
        )

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        self.fields["proxy_date"].widget.attrs.update(
            {
                "id": "datepicker",
            }
        )
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )


# ============================ misc ==============================

# from localflavor.ru.forms import (
#     RUPostalCodeField,
#     RURegionSelect,
#     RUCountySelect,
# ) # noqa: E501

# from localflavor.generic.forms import BICFormField, IBANFormField

# class CompanyDetailViewForm(forms.ModelForm):
#     """Добавить phonenumber."""

#     phone_number = PhoneNumberField(region="RU")

# self.fields["city"].widget.attrs.update(
#     {
#         "id": "tags",
#     }
# )

# self.fields["responsible_offices"].initial = "?"

# region = RURegionSelect()


# class UserProfileGoalForm(forms.ModelForm):
#     class Meta:
#     model = UserProfileGoal
#     ...

#     def clean(self):
#         cleaned_data = super(UserProfileGoalForm, self).clean()
#         if self.instance.pk is not None:
#             return cleaned_data
#         user_profile = self.cleaned_data.get('user_profile')
#         goal_count = user_profile.goals.count()
#         goal_limit = UserGoalConstraint.objects.get(user_profile=user_profile).max_goals # removed try catch for get for easier reading # noqa: E501
#         if goal_count >= goal_limit:
#             raise ValidationError('Maximum limit reached for goals')
#         return cleaned_data

# ============================ end msc ==============================
