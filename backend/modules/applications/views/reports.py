# pylint: disable=line-too-long, unused-argument, too-many-ancestors, too-few-public-methods, invalid-name, too-many-branches, unused-variable, redefined-builtin, too-many-arguments, too-many-locals, too-many-statements  # noqa: E501
"""Представления для модели applications."""

from django.contrib.auth import get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin

# from django.contrib.messages.views import SuccessMessageMixin

# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404

# from django.urls import reverse_lazy
# from django.utils import dateformat

from django.views.generic import (
    TemplateView,
    ListView,
)

# from docxtpl import DocxTemplate


from ..models import (
    # Account,
    Application,
    # Company,
    # Document,
    # Form,
    # Vessel,
    # VesselExtraInfo,
)


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
    paginate_by = 10

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     company = get_object_or_404(Company, slug=self.kwargs["slug"])
    #     return queryset.filter(company=company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Список текущих заявок подразделения"
        # context["company"] = get_object_or_404(
        #     Company, slug=self.kwargs["slug"]
        # )  # noqa: E501
        return context
