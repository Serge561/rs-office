# pylint: disable=too-many-ancestors, line-too-long, super-with-arguments, relative-beyond-top-level, unused-argument # noqa: E501
"""Представления приложения system (for users)."""
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import (
    DetailView,
    UpdateView,
    CreateView,
    TemplateView,
)  # noqa: E501
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import redirect, render
from django.contrib.auth import (
    get_user_model,
    logout,
    update_session_auth_hash,
)  # noqa: E501
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from .forms import (
    UserRegisterForm,
    UserUpdateForm,
    UserLoginForm,
    UserPasswordChangeForm,
    UserForgotPasswordForm,
    UserSetNewPasswordForm,
    FeedbackCreateForm,
)
from .models import Feedback
from ..services.mixins import UserIsNotAuthenticated
from ..services.utils import get_client_ip
from ..services.tasks import (
    send_activate_email_message_task,
    send_contact_email_message_task,
)

User = get_user_model()


class UserRegisterView(UserIsNotAuthenticated, CreateView):
    """Представление регистрации на сайте с формой регистрации."""

    form_class = UserRegisterForm
    success_url = reverse_lazy("home")
    template_name = "system/registration/user_register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Регистрация на сайте"
        return context

    def form_valid(self, form):
        user = form.save(commit=False)  # type: ignore
        user.is_active = False
        user.save()
        send_activate_email_message_task.delay(user.id)
        return redirect("email_confirmation_sent")


class ProfileDetailView(DetailView):
    """Представление для просмотра профиля."""

    model = User
    context_object_name = "profile"
    template_name = "system/profile_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Страница пользователя: {self.object.username}"  # type: ignore # noqa: E501
        return context


class ProfileUpdateView(UpdateView):
    """Представление для редактирования профиля."""

    model = User
    form_class = UserUpdateForm
    template_name = "system/profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "title"
        ] = f"Редактирование профиля пользователя: {self.request.user.username}"  # type: ignore # noqa: E501
        if self.request.POST:
            context["form"] = UserUpdateForm(
                self.request.POST, instance=self.request.user
            )
        else:
            context["form"] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        form = context["form"]

        if form.is_valid():
            form.save()
        else:
            context.update({"form": form})
            return self.render_to_response(context)
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy("profile_detail", kwargs={"slug": self.object.slug})  # type: ignore # noqa: E501


class UserLoginView(SuccessMessageMixin, LoginView):
    """Авторизация на сайте."""

    form_class = UserLoginForm
    template_name = "system/registration/user_login.html"
    next_page = "home"
    success_message = "Добро пожаловать на сайт, %(calculated_field)s."

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            calculated_field=f"{self.request.user.first_name} {self.request.user.patronymic_name}",  # type: ignore # noqa: E501
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Авторизация на сайте"
        return context


def logout_view(request):
    """Выход с сайта."""
    logout(request)
    return HttpResponseRedirect("/login/")


class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """Изменение пароля пользователя."""

    form_class = UserPasswordChangeForm
    template_name = "system/registration/user_password_change.html"
    success_message = "Ваш пароль был успешно изменён!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Изменение пароля на сайте"
        return context

    def get_success_url(self):
        return reverse_lazy(
            "profile_detail", kwargs={"slug": self.request.user.slug}  # type: ignore # noqa: E501
        )  # noqa: E501


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """Представление по сбросу пароля по почте."""

    form_class = UserForgotPasswordForm
    template_name = "system/registration/user_password_reset.html"
    success_url = reverse_lazy("home")
    success_message = "Письмо с инструкцией по восстановлению пароля отправлена на ваш email."  # noqa: E501
    subject_template_name = "system/email/password_subject_reset_mail.txt"
    email_template_name = "system/email/password_reset_mail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Запрос на восстановление пароля"
        return context


class UserPasswordResetConfirmView(
    SuccessMessageMixin, PasswordResetConfirmView
):  # noqa: E501
    """Представление установки нового пароля."""

    form_class = UserSetNewPasswordForm
    template_name = "system/registration/user_password_set_new.html"
    success_url = reverse_lazy("home")
    success_message = "Пароль успешно изменен. Можете авторизоваться на сайте."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Установить новый пароль"
        return context


class UserConfirmEmailView(View):
    """Представление для подтверждения имейла."""

    def get(self, request, uidb64, token):
        """Функционал для подтверждения имейла."""

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(
            user, token
        ):  # noqa: E501
            user.is_active = True
            user.save()
            # login(request, user)
            update_session_auth_hash(request, user)
            return redirect("email_confirmed")
        return redirect("email_confirmation_failed")


class EmailConfirmationSentView(TemplateView):
    """Представление для отправки подтверждения на почту."""

    template_name = "system/registration/email_confirmation_sent.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Письмо активации отправлено"
        return context


class EmailConfirmedView(TemplateView):
    """Представление в случае успешной активации имейла."""

    template_name = "system/registration/email_confirmed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Ваш электронный адрес активирован"
        return context


class EmailConfirmationFailedView(TemplateView):
    """Представление в случае неудачной активации имейла."""

    template_name = "system/registration/email_confirmation_failed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Ваш электронный адрес не активирован"
        return context


def tr_handler404(request, exception):
    """Обработка ошибки 404."""
    return render(
        request=request,
        template_name="system/errors/error_page.html",
        status=404,
        context={
            "title": "Страница не найдена: 404",
            "error_message": "К сожалению такая страница была не найдена, или перемещена",  # noqa: E501
        },
    )


def tr_handler500(request):
    """Обработка ошибки 500."""
    return render(
        request=request,
        template_name="system/errors/error_page.html",
        status=500,
        context={
            "title": "Ошибка сервера: 500",
            "error_message": "Внутренняя ошибка сайта, вернитесь на главную страницу, отчет об ошибке мы направим администрации сайта",  # noqa: E501
        },
    )


def tr_handler403(request, exception):
    """Обработка ошибки 403."""
    return render(
        request=request,
        template_name="system/errors/error_page.html",
        status=403,
        context={
            "title": "Ошибка доступа: 403",
            "error_message": "Доступ к этой странице ограничен",
        },
    )


class FeedbackCreateView(SuccessMessageMixin, CreateView):
    """Представление формы обратной связи."""

    model = Feedback
    form_class = FeedbackCreateForm
    success_message = "Ваше письмо успешно отправлено администрации сайта"
    template_name = "system/feedback.html"
    extra_context = {"title": "Контактная форма"}
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        if form.is_valid():
            feedback = form.save(commit=False)  # type: ignore
            feedback.ip_address = get_client_ip(self.request)
            email = ""
            if self.request.user.is_authenticated:
                feedback.user = self.request.user
                email = self.request.user.email  # type: ignore
            send_contact_email_message_task.delay(
                feedback.subject,
                email,
                feedback.content,
                feedback.ip_address,
                feedback.user_id,
            )
        return super().form_valid(form)
