"""Настройка приложения system."""

from django.apps import AppConfig


class SystemConfig(AppConfig):
    """Конфигурация приложения system."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.system"
    verbose_name = "Система"
