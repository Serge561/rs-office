# pylint: disable=too-few-public-methods, line-too-long, import-error
"""Формы приложения applications."""

from django import forms
from django.contrib.auth import get_user_model
from dal import autocomplete
from .models import (
    Application,
    Vessel,
    VesselExtraInfo,
    Employee,
    Form,
    Document,
    Account,
)

User = get_user_model()


class ApplicationCreateForm(forms.ModelForm):
    """Форма добавления заявки компании."""

    class Meta:
        """Мета форма добавления заявки компании."""

        model = Application
        exclude = (
            "company",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )
        labels = {
            "city": "Место освидетельствования",
        }
        widgets = {
            "city": autocomplete.ModelSelect2(url="city-autocomplete"),  # noqa: E501
            "vessel": autocomplete.ModelSelect2(
                url="vessel-autocomplete"
            ),  # noqa: E501
        }

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind и другая настройка."""
        super().__init__(*args, **kwargs)

        self.fields["date"].widget.attrs.update(
            {
                "id": "datepicker",
            }
        )
        self.fields["completion_date"].widget.attrs.update(
            {
                "id": "datepicker2",
            }
        )
        self.fields["occasional_cause"].widget.attrs.update(
            {
                "rows": 6,
                "placeholder": "указать причину ВНО (в связи с ...)\r\nуказать вид существующего св-ва (ССП/СП/СПЛ) и № для его подтверждения или возобновления\r\nуказать название и № ТД\r\nуказать количество сварщиков или СОТПС\r\nуказать этап строительства",  # noqa: E501
            }
        )
        self.fields["register_signer"].queryset = User.staff.directors(  # type: ignore # noqa: E501
            office_number=self.initial["office_number"]
        )

        self.fields["applicant_signer"].queryset = Employee.objects.get_company_staff(  # type: ignore # noqa: E501
            company=self.initial["company"]
        )

        self.fields["authorized_person"].queryset = Employee.objects.get_company_staff(  # type: ignore # noqa: E501
            company=self.initial["company"]
        )

        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )


class ApplicationUpdateForm(ApplicationCreateForm):
    """Форма обновления заявки предприятия."""

    class Meta:
        """Мета формы обновления заявки предприятия."""

        model = Application
        fields = (
            "number",
            "date",
            "completion_date",
            "survey_code",
            "survey_type",
            "survey_scope",
            "occasional_cause",
            "survey_object",
            "vessel",
            "register_signer",
            "applicant_signer",
            "authorized_person",
        )
        widgets = {
            "vessel": autocomplete.ModelSelect2(
                url="vessel-autocomplete"
            ),  # noqa: E501
        }

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.attrs.update(
            {
                "id": "datepicker",
            }
        )
        self.fields["completion_date"].widget.attrs.update(
            {
                "id": "datepicker2",
            }
        )
        self.fields["occasional_cause"].widget.attrs["rows"] = 5
        self.fields["register_signer"].queryset = User.staff.directors(  # type: ignore # noqa: E501
            office_number=self.initial["office_number"]
        )

        self.fields["applicant_signer"].queryset = Employee.objects.get_company_staff(  # type: ignore # noqa: E501
            company=self.initial["company"]
        )

        self.fields["authorized_person"].queryset = Employee.objects.get_company_staff(  # type: ignore # noqa: E501
            company=self.initial["company"]
        )

        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )


class VesselCreateForm(forms.ModelForm):
    """Форма добавления судна."""

    class Meta:
        """Мета форма добавления судна."""

        model = Vessel
        fields = (
            "name",
            "name_en",
            "rs_number",
            "imo_number",
            "g_tonnage",
            "build_date",
            "me_power",
            "flag",
            "vessel_stat_group",
        )
        widgets = {
            "flag": autocomplete.ListSelect2(url="country-autocomplete"),  # noqa: E501
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


class VesselUpdateForm(forms.ModelForm):
    """Форма добавления судна."""

    class Meta:
        """Мета формы редактирования параметров судна."""

        model = Vessel
        fields = (
            "name",
            "name_en",
            "rs_number",
            "imo_number",
            "g_tonnage",
            "build_date",
            "me_power",
            "flag",
            "vessel_stat_group",
            "is_international_voyage",
        )
        widgets = {
            "flag": autocomplete.ListSelect2(url="country-autocomplete"),  # noqa: E501
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
        self.fields["is_international_voyage"].widget.attrs.update(
            {
                "class": "",
                "autocomplete": "off",
            }
        )


class VesselExtraInfoUpdateForm(forms.ModelForm):
    """Форма обновления доп. инфо по судну и заявке."""

    assigned_surveyors = forms.ModelMultipleChoiceField(
        label="Исполнители заявки",
        queryset=User.staff.surveyors(),  # type: ignore
    )  # noqa: E501

    class Meta:
        """Мета формы обновления доп. инфо по судну и заявке."""

        model = VesselExtraInfo
        fields = (
            "class_status",
            "due_date",
            "city",
            "previous_survey_date",
            "last_psc_inspection_date",
            "last_psc_inspection_result",
            "completion_expected_date",
            "assigned_surveyors",
        )
        labels = {
            "city": "Место предыдущего освидетельствования",
        }
        widgets = {
            "city": autocomplete.ModelSelect2(url="city-autocomplete")  # noqa: E501
        }

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под Tailwind."""
        super().__init__(*args, **kwargs)
        self.fields["last_psc_inspection_result"].widget.attrs["rows"] = 2
        self.fields["due_date"].widget.attrs.update(
            {
                "id": "datepicker",
            }
        )
        self.fields["previous_survey_date"].widget.attrs.update(
            {
                "id": "datepicker2",
            }
        )
        self.fields["last_psc_inspection_date"].widget.attrs.update(
            {
                "id": "datepicker3",
            }
        )
        self.fields["completion_expected_date"].widget.attrs.update(
            {
                "id": "datepicker4",
            }
        )
        self.fields["city"].required = False
        self.fields["assigned_surveyors"].queryset = User.staff.surveyors().filter(  # type: ignore # noqa: E501
            office_number__number__icontains=self.initial["branch_number"]
        )
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-7 border-none mt-0 rounded px-4 w-full bg-gray-50",  # noqa: E501
                    "autocomplete": "off",
                }
            )


# ======================= Form ==========================


class FormCreateForm(forms.ModelForm):
    """Форма добавления формы документа."""

    class Meta:
        """Мета форма добавления формы документа."""

        model = Form
        fields = (
            "number",
            "form_type",
            "description",
        )
        # widgets = {
        #     "flag": autocomplete.ListSelect2(url="country-autocomplete"),  # noqa: E501
        # }

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


class DocumentCreateForm(forms.ModelForm):
    """Форма добавления выданного документа или письма."""

    class Meta:
        """Мета формы добавления выданного документа или письма."""

        model = Document
        fields = (
            # "application",
            "number",
            "form",
            "item_particulars",
        )
        # labels = {
        #     "city": "Место предыдущего освидетельствования",
        # }
        widgets = {
            "form": autocomplete.ListSelect2(url="form-autocomplete"),  # noqa: E501
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


class DocumentUpdateForm(forms.ModelForm):
    """Форма обновления выданного документа или письма."""

    class Meta:
        """Мета формы обновления выданного документа или письма."""

        model = Document
        fields = (
            # "application",
            "number",
            "form",
            "item_particulars",
        )
        # labels = {
        #     "city": "Место предыдущего освидетельствования",
        # }
        widgets = {
            "form": autocomplete.ListSelect2(url="form-autocomplete"),  # noqa: E501
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


# ======================= Account ==========================


class AccountUpdateForm(forms.ModelForm):
    """Форма обновления стоимости услуги."""

    class Meta:
        """Мета формы обновления стоимости услуги."""

        model = Account
        fields = (
            "service_cost",
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
