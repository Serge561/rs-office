# pylint: disable=line-too-long, no-member, too-few-public-methods
"""Миксины пользовательских прав доступа и другие кастомные."""
from django.contrib import messages
from django.shortcuts import redirect
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

User = get_user_model()


class AdminRequiredMixin(AccessMixin):
    """Миксин действий, для которых требуются права админа."""

    def dispatch(self, request, *args, **kwargs):
        """Функция определения прав доступа админа для удаления карточки."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_authenticated:
            if not request.user.is_staff:
                messages.info(
                    request,
                    "Удаление карточки доступно только администратору.",  # noqa: E501
                )  # noqa: E501
                return redirect("home")
        return super().dispatch(request, *args, **kwargs)  # type: ignore


class UserIsNotAuthenticated(UserPassesTestMixin):
    """Миксин для предотвращения посещения страницы регистрации авторизованными пользователями."""  # noqa: E501

    def test_func(self):
        """Сообщение в случае, если пользователь авторизован."""
        if self.request.user.is_authenticated:  # type: ignore
            messages.info(
                self.request,  # type: ignore
                "Вы уже авторизованы. Вы не можете посетить эту страницу.",  # noqa: E501
            )
            raise PermissionDenied
        return True

    def handle_no_permission(self):
        """Перенаправление пользователей без определённых прав доступа."""  # noqa: E501
        if self.request.user.is_authenticated:  # type: ignore
            return redirect("home")
        return redirect("login")


class CreatorMixin(models.Model):
    """
    Миксин пользователя, даты и времени создания
    объектов моделей.
    """

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время создания"
    )
    created_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_DEFAULT,
        related_name="%(app_label)s_%(class)s_related_cr",
        related_query_name="%(app_label)s_%(class)ss_cr",
        verbose_name="Создал",
        default=None,
        null=True,
    )

    class Meta:
        """
        Определение класса примеси даты и времени создания
        модели как абстрактного.
        """

        abstract = True


class UpdaterMixin(models.Model):
    """Миксин пользователя, даты и времени обновления объектов моделей."""

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата и время обновления",
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_related_u",
        related_query_name="%(app_label)s_%(class)ss_u",
        verbose_name="Обновил",
        null=True,
        blank=True,
    )

    class Meta:
        """
        Определение класса примеси даты и
        времени обновления как абстрактного.
        """

        abstract = True
