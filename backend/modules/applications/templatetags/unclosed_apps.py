"""Кастомный тэг шаблона подсчёта количества
    незакрытых заявок."""

from django import template

register = template.Library()


@register.filter()
def unclosed_app_count_filter(value):
    """Кастомный тэг шаблона подсчёта количества
    незакрытых заявок для кнопки 'Показать заявки'."""
    counter = 0
    if value:
        for application in value:
            if application.completion_date is None:
                counter += 1
    return counter
