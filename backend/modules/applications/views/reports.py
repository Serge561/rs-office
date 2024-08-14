# pylint: disable=line-too-long, too-many-ancestors, no-member, too-many-function-args, too-many-statements, too-many-locals  # noqa: E501
"""Представления для модели applications."""

import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Q

# from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    TemplateView,
    ListView,
)
from ..models import Application, Vessel

User = get_user_model()


class DashboardView(LoginRequiredMixin, TemplateView):
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
                # company__responsible_offices__number__icontains=office_number
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (
            f"Освидетельствование судов в эксплуатации в {datetime.date.today().year} году."  # type: ignore # noqa: E501
        )
        qs = self.object_list  # type: ignore

        oiltanker_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.OILTANKER  # noqa: E501
        ).count()
        context["oiltanker"] = oiltanker_sur_count
        oiltanker_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.OILTANKER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["oiltanker_b"] = oiltanker_bottom_count

        oilchemicaltanker_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.OILCHEMTANKER  # noqa: E501
        ).count()
        context["oilchemicaltanker"] = oilchemicaltanker_sur_count
        oilchemicaltanker_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.OILCHEMTANKER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["oilchemicaltanker_b"] = oilchemicaltanker_bottom_count

        chemicaltanker_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.CHEMTANKER  # noqa: E501
        ).count()
        context["chemicaltanker"] = chemicaltanker_sur_count
        chemicaltanker_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.CHEMTANKER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["chemicaltanker_b"] = chemicaltanker_bottom_count

        gascarrier_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.GASCARRIER  # noqa: E501
        ).count()
        context["gascarrier"] = gascarrier_sur_count
        gascarrier_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.GASCARRIER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["gascarrier_b"] = gascarrier_bottom_count

        othertanker_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.OTHERTANKER  # noqa: E501
        ).count()
        context["othertanker"] = othertanker_sur_count
        othertanker_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.OTHERTANKER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["othertanker_b"] = othertanker_bottom_count

        oilorecarrier_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.OILORECARRIER  # noqa: E501
        ).count()
        context["oilorecarrier"] = oilorecarrier_sur_count
        oilorecarrier_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.OILORECARRIER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["oilorecarrier_b"] = oilorecarrier_bottom_count

        oilcarrierbulker_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.ORECARRBULKER  # noqa: E501
        ).count()
        context["oilcarrierbulker"] = oilcarrierbulker_sur_count
        oilcarrierbulker_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.ORECARRBULKER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["oilcarrierbulker_b"] = oilcarrierbulker_bottom_count

        generalcargo_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.GENERALCARGO  # noqa: E501
        ).count()
        context["generalcargo"] = generalcargo_sur_count
        generalcargo_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.GENERALCARGO  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["generalcargo_b"] = generalcargo_bottom_count

        cargopassanger_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.CARGOPASSANGER  # noqa: E501
        ).count()
        context["cargopassanger"] = cargopassanger_sur_count
        cargopassanger_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.CARGOPASSANGER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["cargopassanger_b"] = cargopassanger_bottom_count

        containership_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.CONTAINERSHIP  # noqa: E501
        ).count()
        context["containership"] = containership_sur_count
        containership_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.CONTAINERSHIP  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["containership_b"] = containership_bottom_count

        carcarrier_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.CARCARRIER  # noqa: E501
        ).count()
        context["carcarrier"] = carcarrier_sur_count
        carcarrier_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.CARCARRIER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["carcarrier_b"] = carcarrier_bottom_count

        fishtransport_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.FISHTRANSPORT  # noqa: E501
        ).count()
        context["fishtransport"] = fishtransport_sur_count
        fishtransport_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.FISHTRANSPORT  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["fishtransport_b"] = fishtransport_bottom_count

        fishingvessel_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.FISHINGVESSEL  # noqa: E501
        ).count()
        context["fishingvessel"] = fishingvessel_sur_count
        fishingvessel_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.FISHINGVESSEL  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["fishingvessel_b"] = fishingvessel_bottom_count

        passangership_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.PASSANGERSHIP  # noqa: E501
        ).count()
        context["passangership"] = passangership_sur_count
        passangership_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.PASSANGERSHIP  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["passangership_b"] = passangership_bottom_count

        supplier_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.SUPPLER  # noqa: E501
        ).count()
        context["supplier"] = supplier_sur_count
        supplier_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.SUPPLER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )
        context["supplier_b"] = supplier_bottom_count

        tug_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.TUG  # noqa: E501
        ).count()  # noqa: E501
        context["tug"] = tug_sur_count
        tug_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.TUG  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )  # noqa: E501
        context["tug_b"] = tug_bottom_count

        dradger_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.DRADGER  # noqa: E501
        ).count()  # noqa: E501
        context["dradger"] = dradger_sur_count
        dradger_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.DRADGER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )  # noqa: E501
        context["dradger_b"] = dradger_bottom_count

        reefer_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.REEFER  # noqa: E501
        ).count()  # noqa: E501
        context["reefer"] = reefer_sur_count
        reefer_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.REEFER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )  # noqa: E501
        context["reefer_b"] = reefer_bottom_count

        icebreaker_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.ICEBRAKER  # noqa: E501
        ).count()  # noqa: E501
        context["icebreaker"] = icebreaker_sur_count
        icebreaker_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.ICEBRAKER  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )  # noqa: E501
        context["icebreaker_b"] = icebreaker_bottom_count

        researchship_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.RESEARCHSHIP  # noqa: E501
        ).count()  # noqa: E501
        context["researchship"] = researchship_sur_count
        researchship_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.RESEARCHSHIP  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )  # noqa: E501
        context["researchship_b"] = researchship_bottom_count

        othership_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.OTHERSHIP  # noqa: E501
        ).count()  # noqa: E501
        context["othership"] = othership_sur_count
        othership_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.OTHERSHIP  # noqa: E501
            )
            .filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .count()
        )  # noqa: E501
        context["othership_b"] = othership_bottom_count

        smallcraft_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.SMALLCRAFT  # noqa: E501
        ).count()  # noqa: E501
        context["smallcraft"] = smallcraft_sur_count
        smallcraft_bottom_count = (
            qs.filter(
                vessel__vessel_stat_group=Vessel.VesselStatGroup.SMALLCRAFT  # noqa: E501
            )
            .filter(
                survey_scope__in=[
                    Application.SurveyScope.SPECIL,
                    Application.SurveyScope.RENEWL,
                    Application.SurveyScope.INITIL,
                ]
            )
            .count()
        )  # noqa: E501
        context["smallcraft_b"] = smallcraft_bottom_count

        pipeline_sur_count = qs.filter(
            vessel__vessel_stat_group=Vessel.VesselStatGroup.PIPELINE  # noqa: E501
        ).count()  # noqa: E501
        context["pipeline"] = pipeline_sur_count

        total_apps = qs.count()
        context["total"] = total_apps
        total_bottom = (
            qs.filter(survey_scope__in=HIGHLY_LIKELY_BOTTOM_SURVEY)
            .exclude(
                Q(vessel__vessel_stat_group=Vessel.VesselStatGroup.SMALLCRAFT)
                & Q(survey_scope=Application.SurveyScope.INTERM)
            )  # noqa: E501
            .count()
        )
        context["total_b"] = total_bottom

        initial_sur_count = qs.filter(
            survey_scope=Application.SurveyScope.INITIL
        ).count()
        context["initial"] = initial_sur_count

        special_sur_count = qs.filter(
            survey_scope=Application.SurveyScope.SPECIL
        ).count()
        context["special"] = special_sur_count

        intermediate_sur_count = qs.filter(
            survey_scope=Application.SurveyScope.INTERM
        ).count()
        context["intermediate"] = intermediate_sur_count
        intermediate_bottom_count = (
            qs.filter(survey_scope=Application.SurveyScope.INTERM)
            .exclude(
                Q(vessel__vessel_stat_group=Vessel.VesselStatGroup.SMALLCRAFT)
                & Q(survey_scope=Application.SurveyScope.INTERM)
            )
            .count()
        )
        context["intermediate_b"] = intermediate_bottom_count

        annual_sur_count = qs.filter(
            survey_scope=Application.SurveyScope.ANNUAL
        ).count()
        context["annual"] = annual_sur_count

        occasional_sur_count = qs.filter(
            survey_scope=Application.SurveyScope.OCCASL
        ).count()
        context["occasional"] = occasional_sur_count

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
                    datetime.date(current_year, current_month, 1),
                    datetime.date.today(),
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        start_date = datetime.date(current_year, current_month, 1).strftime(
            "%d.%m.%Y"
        )  # noqa: E501
        context["title"] = (
            f'Перечень выполненных заявок в промышленности инспектором {self.request.user.username} c {start_date} по {datetime.date.today().strftime("%d.%m.%Y")}'  # type: ignore # noqa: E501
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
                    datetime.date(current_year, current_month, 1),
                    datetime.date.today(),
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        start_date = datetime.date(current_year, current_month, 1).strftime(
            "%d.%m.%Y"
        )  # noqa: E501
        context["title"] = (
            f'Перечень выполненных заявок по рассмотрению документации инспектором {self.request.user.username} c {start_date} по {datetime.date.today().strftime("%d.%m.%Y")}'  # type: ignore # noqa: E501
        )
        return context
