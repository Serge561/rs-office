# pylint: disable={C0115, E1121, E0401}
"""Админ-панель приложения system (users)."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import OfficeNumber, Position, Feedback
from .forms import CustomUserCreationForm, CustomUserChangeForm

User = get_user_model()


class OfficeNumberAdmin(admin.ModelAdmin):
    model = OfficeNumber
    list_display = [
        "id",
        "name",
        "number",
    ]
    search_fields = ["name"]


class PositionAdmin(admin.ModelAdmin):
    model = Position
    list_display = [
        "id",
        "name",
    ]


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = [
        "id",
        "username",
        "email",
        "slug",
    ]
    list_display_links = ("username", "slug")
    readonly_fields = ("id",)

    fieldsets = (
        (None, {"fields": ("id", "username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "last_name",
                    "first_name",
                    "patronymic_name",
                    "email",
                    "slug",
                )
            },
        ),
        (
            "Extra info",
            {
                "fields": (
                    "office_number",
                    "position",
                    "phone_number",
                    "proxy_number",
                    "proxy_date",
                    # "extra_info",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    # "groups",
                    # "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     form.base_fields["username"].label = "Имя пользователя"
    #     ==============It doesn't work.===============
    #     form.base_fields["password"].label = "Пароль"
    #     =============================================
    #     return form


class FeedbackAdmin(admin.ModelAdmin):
    """
    Админ-панель модели профиля
    """

    list_display = ("email", "ip_address", "user")
    list_display_links = ("email", "ip_address")


admin.site.register(User, CustomUserAdmin)
admin.site.register(OfficeNumber, OfficeNumberAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Feedback, FeedbackAdmin)
