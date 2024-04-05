"""Конфигурация приложения companies."""

from django.apps import AppConfig


class CompaniesConfig(AppConfig):
    """Конфигурация приложения companies."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.companies"
    verbose_name = "Компании"
