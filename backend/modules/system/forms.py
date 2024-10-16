# pylint: disable=too-many-ancestors, too-few-public-methods, line-too-long
"""Импорт форм для админ-панели и создание остальных форм."""
# import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
    SetPasswordForm,
    PasswordResetForm,
)
from .models import Feedback


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Форма создания пользователя в админ-панели."""

    class Meta:
        """Поля формы создания пользователя."""

        model = User
        fields = ("username",)


class CustomUserChangeForm(UserChangeForm):
    """Форма изменения профиля пользователя в админ-панели."""

    class Meta:
        """Поля формы изменения пользователя."""

        model = User
        fields = ("username",)


class UserUpdateForm(forms.ModelForm):
    """Форма обновления данных пользователя"""

    class Meta:
        """Мета формы обновления данных пользователя."""

        model = User
        fields = (
            "username",
            "last_name",
            "first_name",
            "patronymic_name",
            "first_name_en",
            "last_name_en",
            "position",
            "office_number",
            "phone_number",
            "email",
            "proxy_number",
            "proxy_date",
        )

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под tailwind."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "h-10 border mt-1 rounded px-4 w-full bg-gray-50",
                    "autocomplete": "off",
                }
            )
        self.fields["username"].widget = forms.HiddenInput()
        self.fields["proxy_date"].widget.attrs.update(
            {
                "id": "datepicker",
            }
        )
        current_user = self.instance
        if current_user.groups.filter(name__iexact="guest").exists():  # noqa: E501
            self.fields["position"].widget = forms.HiddenInput()
            self.fields["first_name_en"].widget = forms.HiddenInput()
            self.fields["last_name_en"].widget = forms.HiddenInput()
            self.fields["office_number"].widget = forms.HiddenInput()
            self.fields["proxy_number"].widget = forms.HiddenInput()
            self.fields["proxy_date"].widget = forms.HiddenInput()

    def clean_email(self):
        """Проверка email на уникальность."""
        email = self.cleaned_data.get("email")
        username = self.cleaned_data.get("username")
        if (
            email
            and User.objects.filter(email=email)
            .exclude(username=username)
            .exists()  # noqa: E501
        ):
            raise forms.ValidationError("Email адрес должен быть уникальным")
        return email


class UserRegisterForm(UserCreationForm):
    """Переопределенная форма регистрации пользователя."""

    class Meta(CustomUserCreationForm.Meta):
        """Мета формы регистрации пользователя."""

        model = User
        fields = CustomUserCreationForm.Meta.fields + (
            "email",
            "first_name",
            "last_name",
            "office_number",
        )  # type: ignore # noqa: E501

    def clean_email(self):
        """Проверка email на уникальность."""
        email = self.cleaned_data.get("email")
        username = self.cleaned_data.get("username")
        if (
            email
            and User.objects.filter(email=email)
            .exclude(username=username)
            .exists()  # noqa: E501
        ):
            raise forms.ValidationError(
                "Такой email уже используется в системе"
            )  # noqa: E501
        return email

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы регистрации."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields["username"].widget.attrs.update(
                {"placeholder": "Придумайте свой логин"}
            )
            self.fields["email"].widget.attrs.update(
                {"placeholder": "Введите свой email"}
            )
            self.fields["first_name"].widget.attrs.update(
                {"placeholder": "Ваше имя"}
            )  # noqa: E501
            self.fields["last_name"].widget.attrs.update(
                {"placeholder": "Ваша фамилия"}
            )
            self.fields["office_number"].widget.attrs.update(
                {"placeholder": "Участок"}
            )  # noqa: E501
            self.fields["password1"].widget.attrs.update(
                {"placeholder": "Придумайте свой пароль"}
            )
            self.fields["password2"].widget.attrs.update(
                {"placeholder": "Повторите придуманный пароль"}
            )
            self.fields[field].widget.attrs.update(
                {
                    "class": "border rounded-lg px-3 py-2 mt-0 mb-2 text-sm w-full",  # noqa: E501
                    "autocomplete": "off",
                }
            )


# class UserLoginForm(AuthenticationForm):
#     """Форма авторизации на сайте."""

#     def __init__(self, *args, **kwargs):
#         """Обновление стилей формы авторизации."""
#         super().__init__(*args, **kwargs)
#         self.fields["username"].widget.attrs[
#             "placeholder"
#         ] = "Логин пользователя"  # noqa: E501
#         self.fields["password"].widget.attrs[
#             "placeholder"
#         ] = "Пароль пользователя"  # noqa: E501
#         self.fields["username"].label = "Логин"
#         for field in self.fields:
#             self.fields[field].widget.attrs.update(
#                 {
#                     "class": "border rounded-lg px-3 py-2 mt-1 mb-2 text-sm w-full",  # noqa: E501
#                     "autocomplete": "off",
#                 }
#             )


class UserLoginForm(AuthenticationForm):
    """Форма авторизации на сайте."""

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы авторизации."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "block w-full px-4 py-2 mt-1 mb-3 text-gray-700 placeholder-gray-400 bg-white border border-gray-200 rounded-md dark:placeholder-gray-600 dark:bg-gray-900 dark:text-gray-300 dark:border-gray-700 focus:border-blue-400 dark:focus:border-blue-400 focus:ring-blue-400 focus:outline-none focus:ring focus:ring-opacity-40",  # noqa: E501
                    "autocomplete": "off",
                }
            )


class UserPasswordChangeForm(SetPasswordForm):
    """Форма изменения пароля."""

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "border rounded-lg px-3 py-2 mt-1 mb-2 text-sm w-full",  # noqa: E501
                    "autocomplete": "off",
                }
            )


class UserForgotPasswordForm(PasswordResetForm):
    """Запрос на восстановление пароля."""

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "border rounded-lg px-3 py-2 mt-1 mb-2 text-sm w-full",  # noqa: E501
                    "autocomplete": "off",
                }
            )


class UserSetNewPasswordForm(SetPasswordForm):
    """Изменение пароля пользователя после подтверждения."""

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "border rounded-lg px-3 py-2 mt-1 mb-2 text-sm w-full",  # noqa: E501
                    "autocomplete": "off",
                }
            )


class FeedbackCreateForm(forms.ModelForm):
    """Форма отправки обратной связи."""

    class Meta:
        """Мета фориы обратной связи."""

        model = Feedback
        fields = ("subject", "email", "content")

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы
        """
        super().__init__(*args, **kwargs)
        self.fields["subject"].widget.attrs.update(
            {"placeholder": "Введите тему письма"}
        )  # noqa: E501
        # self.fields["email"].widget.attrs.update(
        #     {"placeholder": "john.doe@rs-class.org"}
        # )
        self.fields["email"].widget = forms.HiddenInput()
        self.fields["content"].widget.attrs.update(
            {"placeholder": "Введите текст сообщения"}
        )
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": "w-full px-3 py-2 border rounded-md focus:outline-none focus:border-blue-500",  # noqa: E501
                    "autocomplete": "off",
                }
            )
