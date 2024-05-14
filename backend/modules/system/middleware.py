# pylint: disable=too-few-public-methods, line-too-long
"""Представление статуса пользователей."""

# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()


class ActiveUserMiddleware(MiddlewareMixin):
    """Функция определения статуса пользователей."""

    def process_request(self, request):
        """Проверка авторизован ли пользователь и имеет ли его сессия уникальный идентификатор session_key."""  # noqa: E501
        if request.user.is_authenticated and request.session.session_key:
            cache_key = f"last-seen-{request.user.id}"
            last_login = cache.get(cache_key)

            if not last_login:
                User.objects.filter(id=request.user.id).update(
                    last_login=timezone.now()
                )
                # Устанавливаем кэширование на 300 секунд с текущей датой по ключу last-seen-id-пользователя  # noqa: E501
                cache.set(cache_key, timezone.now(), 300)
