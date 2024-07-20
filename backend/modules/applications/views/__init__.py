# pylint: disable=import-error
"""Модуль пакета представлений приложения applications."""

from modules.services.mixins import AdminRequiredMixin  # noqa: F401
from ..forms import *  # noqa: F401, F403
from .views import *  # noqa: F401, F403
from .reports import *  # noqa: F401, F403
from .prints import *  # noqa: F401, F403
