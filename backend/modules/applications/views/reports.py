# pylint: disable=line-too-long, too-many-ancestors, no-member, too-many-function-args, too-many-statements, too-many-locals, import-error  # noqa: E501
"""Представления для модели applications-отчёты."""

import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from django.views.generic import (
    TemplateView,
    ListView,
)

from modules.system.models import OfficeNumber
from modules.services.mixins import RSUserOnlyMixin
from ..models import Application, Vessel

User = get_user_model()


class DashboardView(RSUserOnlyMixin, TemplateView):
    """Представление для вывода кнопочной формы управления отчётами."""

    login_url = "login"
    template_name = "applications/reports/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Панель управления отчётами"
        return context


class CurrentApplicationsView(LoginRequiredMixin, ListView):
    """Представление для вывода списка текущих заявок подразделения."""

    model = Application
    template_name = "applications/reports/current_applications.html"
    login_url = "login"
    context_object_name = "applications"
    # paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        office_number = user.office_number.number  # type: ignore
        return (
            queryset.exclude(completion_date__isnull=False)
            .filter(
                survey_code__in=[
                    Application.SurveyCode.C00001,
                    Application.SurveyCode.C00002,
                    Application.SurveyCode.C00121,
                ]
            )
            .filter(
                vesselextrainfo__assigned_surveyors__office_number__number__icontains=office_number  # noqa: E501
            )
            .distinct()  # noqa: E501
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (
            f'Перечень судов в ремонте и постройке в зоне деятельности подразделения "{self.request.user.office_number}" по состоянию на {datetime.date.today().strftime("%d.%m.%Y")}'  # type: ignore # noqa: E501
        )
        return context


class CurrentApplicationsSurveyorView(LoginRequiredMixin, ListView):
    """Представление для вывода списка текущих заявок инспектора
    по судам."""

    model = Application
    template_name = "applications/reports/current_applications_surveyor.html"
    login_url = "login"
    context_object_name = "applications"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        return (
            queryset.exclude(completion_date__isnull=False)
            .filter(
                survey_code__in=[
                    Application.SurveyCode.C00001,
                    Application.SurveyCode.C00002,
                    Application.SurveyCode.C00121,
                ]
            )
            .filter(
                vesselextrainfo__assigned_surveyors__pk__in=[user.id]  # type: ignore # noqa: E501
            )  # noqa: E501
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (
            f'Перечень судов в ремонте и постройке инспектора {self.request.user.username} по состоянию на {datetime.date.today().strftime("%d.%m.%Y")}'  # type: ignore # noqa: E501
        )
        return context


HIGHLY_LIKELY_BOTTOM_SURVEY = (
    Application.SurveyScope.BOTTOM,
    Application.SurveyScope.SPECIL,
    Application.SurveyScope.RENEWL,
    Application.SurveyScope.INTERM,
    Application.SurveyScope.INITIL,
)


class AnnualReportView(LoginRequiredMixin, ListView):
    """Представление для вывода годового отчёта."""

    model = Application
    template_name = "applications/reports/annual_report.html"
    login_url = "login"
    context_object_name = "applications"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        office_number = user.office_number.number  # type: ignore
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        if current_month == 1:
            current_or_last_year = current_year - 1  # type: ignore
        else:
            current_or_last_year = current_year
        return (
            queryset.exclude(completion_date__isnull=True)
            .filter(
                survey_code__in=[
                    Application.SurveyCode.C00001,
                    Application.SurveyCode.C00016,
                    Application.SurveyCode.C00121,
                ]
            )
            .filter(
                vesselextrainfo__assigned_surveyors__office_number__number__icontains=office_number  # noqa: E501
            )
            .filter(
                completion_date__range=(
                    datetime.date(current_or_last_year, 1, 1),
                    datetime.date.today(),
                )
            )
            .distinct()  # noqa: E501
        )

    def get_survey_number(self, statistical_group, is_bottom):
        """Получить количество освидетельствований по
        статистическим группам судов."""
        qs = self.object_list  # type: ignore
        stat_group_filter = qs.filter(
            vessel__vessel_stat_group=statistical_group  # noqa: E501
        )
        if not is_bottom:
            return stat_group_filter.count()
        if statistical_group == "SMC":
            return stat_group_filter.filter(
                survey_scope__in=[
                    Application.SurveyScope.SPECIL,
                    Application.SurveyScope.RENEWL,
                    Application.SurveyScope.INITIL,
                ]
            ).count()
        return stat_group_filter.filter(
            survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY
        ).count()

    def get_survey_number_by_type(self, survey_type):
        """Получить количество освидетельствований по виду."""
        qs = self.object_list  # type: ignore
        return qs.filter(survey_scope=survey_type).count()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (
            f"Освидетельствование судов в эксплуатации в {datetime.date.today().year} году."  # type: ignore # noqa: E501
        )
        qs = self.object_list  # type: ignore

        for st_gr in Vessel.VesselStatGroup:
            context[f"{st_gr}"] = self.get_survey_number(st_gr, False)
            context[f"{st_gr}_b"] = self.get_survey_number(st_gr, True)

        context["total"] = qs.count()
        context["total_b"] = (
            qs.filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .exclude(
                Q(vessel__vessel_stat_group=Vessel.VesselStatGroup.SMALLCRAFT)
                & Q(survey_scope=Application.SurveyScope.INTERM)
            )  # noqa: E501
            .count()
        )

        for survey in Application.SurveyScope:
            context[f"{survey}"] = self.get_survey_number_by_type(survey)

        context["intermediate_b"] = (
            qs.filter(survey_scope=Application.SurveyScope.INTERM)
            .exclude(
                Q(vessel__vessel_stat_group=Vessel.VesselStatGroup.SMALLCRAFT)
                & Q(survey_scope=Application.SurveyScope.INTERM)
            )
            .count()
        )

        # Количество освидетельствований судов
        # без учёта заявок только на освидетельствование
        # подводной части.
        total_sur_without_only_bottom = qs.exclude(
            survey_scope=Application.SurveyScope.BOTTOM
        ).count()
        context["total_without_only_bottom"] = total_sur_without_only_bottom

        # Количество освидетельствований подводной части
        # при первоначальных, очередных и промежуточных
        # освидетельствованиях (без учёта заявок только
        # на освидетельствование подводной части).
        total_sur_wo_only_b_including_bottom = (
            qs.filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .exclude(survey_scope=Application.SurveyScope.BOTTOM)
            .exclude(
                Q(vessel__vessel_stat_group=Vessel.VesselStatGroup.SMALLCRAFT)
                & Q(survey_scope=Application.SurveyScope.INTERM)
            )  # noqa: E501
            .count()
        )
        context["total_including_bottom"] = (
            total_sur_wo_only_b_including_bottom  # noqa: E501
        )

        return context


class IndustryApplicationsSurveyorView(LoginRequiredMixin, ListView):
    """Представление для вывода списка заявок инспектора
    в промышленности за определённый период."""

    model = Application
    template_name = "applications/reports/industry_applications_surveyor.html"
    login_url = "login"
    context_object_name = "applications"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        if not self.request.GET["start_date"]:
            first_date = datetime.date(current_year, current_month, 1)
        else:
            first_date = self.request.GET["start_date"]
        return (
            queryset.exclude(completion_date__isnull=True)
            .filter(
                survey_code__in=[
                    Application.SurveyCode.C00004,
                    Application.SurveyCode.C00005,
                    Application.SurveyCode.C00009,
                    Application.SurveyCode.C00010,
                    Application.SurveyCode.C00013,
                    Application.SurveyCode.C00015,
                    Application.SurveyCode.C00101,
                    Application.SurveyCode.C00102,
                    Application.SurveyCode.C00103,
                    Application.SurveyCode.C00104,
                    Application.SurveyCode.C00105,
                ]
            )
            .filter(
                vesselextrainfo__assigned_surveyors__pk__in=[user.id]  # type: ignore # noqa: E501
            )  # noqa: E501
            .filter(
                completion_date__range=(
                    first_date,
                    datetime.date.today(),
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        if not self.request.GET["start_date"]:
            first_date = datetime.date(
                current_year, current_month, 1
            ).strftime(  # noqa: E501
                "%d.%m.%Y"
            )
        else:
            start_date = self.request.GET["start_date"]
            first_date = datetime.datetime.strptime(
                start_date, "%Y-%m-%d"
            ).strftime(  # noqa: E501
                "%d.%m.%Y"
            )
        context["title"] = (
            f'Перечень выполненных заявок в промышленности инспектором {self.request.user.username} c {first_date} по {datetime.date.today().strftime("%d.%m.%Y")}'  # type: ignore # noqa: E501
        )
        return context


class DocReviewApplicationsSurveyorView(LoginRequiredMixin, ListView):
    """Представление для вывода списка выполненных заявок инспектора
    по рассмотрению документации за определённый период."""

    model = Application
    template_name = (
        "applications/reports/doc_review_applications_surveyor.html"  # noqa: E501
    )
    login_url = "login"
    context_object_name = "applications"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        if not self.request.GET["start_date"]:
            first_date = datetime.date(current_year, current_month, 1)
        else:
            first_date = self.request.GET["start_date"]
        return (
            queryset.exclude(completion_date__isnull=True)
            .filter(
                survey_code__in=[
                    Application.SurveyCode.C00006,
                ]
            )
            .filter(
                vesselextrainfo__assigned_surveyors__pk__in=[user.id]  # type: ignore # noqa: E501
            )  # noqa: E501
            .filter(
                completion_date__range=(
                    first_date,
                    datetime.date.today(),
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        if not self.request.GET["start_date"]:
            first_date = datetime.date(
                current_year, current_month, 1
            ).strftime(  # noqa: E501
                "%d.%m.%Y"
            )
        else:
            start_date = self.request.GET["start_date"]
            first_date = datetime.datetime.strptime(
                start_date, "%Y-%m-%d"
            ).strftime(  # noqa: E501
                "%d.%m.%Y"
            )
        context["title"] = (
            f'Перечень выполненных заявок по рассмотрению документации инспектором {self.request.user.username} c {first_date} по {datetime.date.today().strftime("%d.%m.%Y")}'  # type: ignore # noqa: E501
        )
        return context


class ShipsInServiceApplicationsSurveyorView(LoginRequiredMixin, ListView):
    """Представление для вывода списка заявок инспектора
    по судам в эксплуатации за определённый период."""

    model = Application
    template_name = (
        "applications/reports/ships_in_service_applications_surveyor.html"  # noqa: E501
    )
    login_url = "login"
    context_object_name = "applications"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        if not self.request.GET["start_date"]:
            first_date = datetime.date(current_year, current_month, 1)
        else:
            first_date = self.request.GET["start_date"]
        return (
            queryset.exclude(completion_date__isnull=True)
            .filter(
                survey_code__in=[
                    Application.SurveyCode.C00001,
                    Application.SurveyCode.C00121,
                ]
            )
            .filter(
                vesselextrainfo__assigned_surveyors__pk__in=[user.id]  # type: ignore # noqa: E501
            )  # noqa: E501
            .filter(
                completion_date__range=(
                    first_date,
                    datetime.date.today(),
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        if not self.request.GET["start_date"]:
            first_date = datetime.date(
                current_year, current_month, 1
            ).strftime(  # noqa: E501
                "%d.%m.%Y"
            )
        else:
            start_date = self.request.GET["start_date"]
            first_date = datetime.datetime.strptime(
                start_date, "%Y-%m-%d"
            ).strftime(  # noqa: E501
                "%d.%m.%Y"
            )
        context["title"] = (
            f'Перечень выполненных заявок по судам в эксплуатации инспектором {self.request.user.username} c {first_date} по {datetime.date.today().strftime("%d.%m.%Y")}'  # type: ignore # noqa: E501
        )
        return context


class InputDateSiSView(LoginRequiredMixin, TemplateView):
    """Представление для вывода модального окна для
    ввода начальной даты отчёта по заявкам по судам в экспл."""

    login_url = "login"
    template_name = "applications/reports/input_date_modal_sis.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Введите начальную дату отчётного периода"
        return context


class InputDateIndustryView(LoginRequiredMixin, TemplateView):
    """Представление для вывода модального окна для
    ввода начальной даты отчёта по заявкам в промышленности."""

    login_url = "login"
    template_name = "applications/reports/input_date_modal_industry.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Введите начальную дату отчётного периода"
        return context


class InputDateDocReviewView(LoginRequiredMixin, TemplateView):
    """Представление для вывода модального окна для
    ввода начальной даты отчёта по заявкам по рассмотрению техдокум."""

    login_url = "login"
    template_name = "applications/reports/input_date_modal_doc_review.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Введите начальную дату отчётного периода"
        return context


class SISByOfficeDashboardView(LoginRequiredMixin, ListView):
    """Представление для вывода списка филиалов подразделения."""

    model = OfficeNumber
    template_name = "applications/reports/sis_by_office_dashboard.html"
    login_url = "login"
    context_object_name = "office_numbers"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        branch_number = user.office_number.number[0:3]  # type: ignore
        return queryset.filter(number__icontains=branch_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (
            "Перечень участков филиала со ссылками на отчёты по текущим заявкам по судам в эксплуатации"  # noqa: E501
        )
        return context


class CurrentApplicationsByOfficeView(LoginRequiredMixin, ListView):
    """Представление для вывода списка текущих
    заявок подразделения по участкам."""

    model = Application
    template_name = "applications/reports/current_applications_by_office.html"
    login_url = "login"
    context_object_name = "applications"

    def get_queryset(self):
        queryset = super().get_queryset()
        office_number = self.request.GET["office_No"]
        return (
            queryset.exclude(completion_date__isnull=False)
            .filter(
                survey_code__in=[
                    Application.SurveyCode.C00001,
                    Application.SurveyCode.C00002,
                    Application.SurveyCode.C00121,
                ]
            )
            .filter(
                vesselextrainfo__assigned_surveyors__office_number__number__icontains=office_number  # noqa: E501
            )
            .distinct()  # noqa: E501
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        office_number = self.request.GET["office_No"]
        context["title"] = (
            f'Перечень судов в ремонте и постройке в зоне деятельности подразделения "{office_number}" по состоянию на {datetime.date.today().strftime("%d.%m.%Y")}'  # type: ignore # noqa: E501
        )
        return context
