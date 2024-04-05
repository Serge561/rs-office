# pylint: disable=unused-argument, line-too-long
"""asdasdasdasdasd."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Application, VesselExtraInfo


@receiver(post_save, sender=Application)
def application_created(sender, instance, created, **kwargs):
    """
    Автоматически создать таблицу с дополнительными сведениями
    по судну и заявке сразу после создания новой заявки.
    """
    # Проверка того, что создана новая заявка
    if created:
        new_extravesselinfo = VesselExtraInfo.objects.create(
            application=instance
        )  # noqa: E501
        # Сохраняем экземпляр
        new_extravesselinfo.save()
