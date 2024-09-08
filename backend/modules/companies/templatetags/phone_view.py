"""Кастомный тэг шаблона, чтобы получить отображение телефонного
    номера в формах на чтение в международном формате."""

from django import template
from phonenumber_field.phonenumber import PhoneNumber

register = template.Library()


@register.filter()
def phone_number_view_filter(value):
    """Кастомный тэг шаблона, чтобы получить отображение телефонного
    номера в формах на чтение в международном формате."""
    if value is None or value == "":
        return ""
    if str(value)[0] == "8":
        corrected_value = f"+7{str(value)[1:]}"
        number = PhoneNumber.from_string(corrected_value)
        return number.as_international
    number = PhoneNumber.from_string(str(value))
    return number.as_international
