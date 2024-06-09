# pylint: disable=line-too-long, too-many-ancestors
"""Представления для модели applications."""

from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

# from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    TemplateView,
    ListView,
)
from ..models import Application

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
            .filter(survey_code__in=["00001", "00002", "00121"])
            .filter(
                # company__responsible_offices__number__icontains=office_number
                vesselextrainfo__assigned_surveyors__office_number__number__icontains=office_number  # noqa: E501
            )
            .distinct()  # noqa: E501
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (
            f'Перечень судов в ремонте и постройке в зоне деятельности подразделения "{self.request.user.office_number}" по состоянию на {datetime.now().strftime("%d.%m.%Y")}'  # type: ignore # noqa: E501
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
            .filter(survey_code__in=["00001", "00002", "00121"])
            .filter(
                vesselextrainfo__assigned_surveyors__pk__in=[user.id]  # type: ignore # noqa: E501
            )  # noqa: E501
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (
            f'Перечень судов в ремонте и постройке инспектора {self.request.user.username} по состоянию на {datetime.now().strftime("%d.%m.%Y")}'  # type: ignore # noqa: E501
        )
        return context
