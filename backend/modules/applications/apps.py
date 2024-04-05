# pylint: disable=import-error, import-outside-toplevel, unused-import
"""Конфигурация приложения applications."""

from django.apps import AppConfig


class ApplicationsConfig(AppConfig):
    """Конфигурация приложения applications."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.applications"
    verbose_name = "Заявки"

    def ready(self):
        import modules.applications.signals  # noqa: F401
