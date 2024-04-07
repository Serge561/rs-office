# pylint: disable=unused-argument, line-too-long
"""asdasdasdasdasd."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models import Application, VesselExtraInfo, Account


@receiver(post_save, sender=Application)
def application_created(sender, instance, created, **kwargs):
    """
    Автоматически создать записи с дополнительными сведениями
    по судну и заявке, а также по стоимости услуги сразу после
    создания новой заявки.
    """
    # Проверка того, что создана новая заявка
    if created:
        new_extravesselinfo = VesselExtraInfo.objects.create(
            application=instance
        )  # noqa: E501
        # Сохраняем экземпляр
        new_extravesselinfo.save()
        # Сохдаём новый объект Account и сохраняем результат
        new_account = Account.objects.create(application=instance)
        new_account.save()
