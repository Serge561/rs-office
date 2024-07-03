"""Кастомный тэг шаблона, чтобы получить только часть
объёма освидетельствования на русском языке для отчётов."""

from django import template

register = template.Library()


@register.filter()
def cut_en_part_filter(value):
    """Кастомный тэг шаблона, чтобы получить только часть
    объёма освидетельствования на русском языке."""
    if value:
        result = str(value).split("/", maxsplit=1)[0]
    return result
