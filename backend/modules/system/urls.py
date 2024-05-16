"""URLs приложения system."""

from django.urls import path

from .views import (
    ProfileUpdateView,
    ProfileDetailView,
    UserRegisterView,
    UserLoginView,
    logout_view,
    UserPasswordChangeView,
    UserForgotPasswordView,
    UserPasswordResetConfirmView,
    EmailConfirmationSentView,
    UserConfirmEmailView,
    EmailConfirmedView,
    EmailConfirmationFailedView,
    FeedbackCreateView,
)


urlpatterns = [
    path("user/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path(
        "user/<str:slug>/", ProfileDetailView.as_view(), name="profile_detail"
    ),  # noqa: E501
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path(
        "password-change/",
        UserPasswordChangeView.as_view(),
        name="password_change",  # noqa: E501
    ),  # noqa: E501
    path(
        "password-reset/",
        UserForgotPasswordView.as_view(),
        name="password_reset",  # noqa: E501
    ),  # noqa: E501
    path(
        "set-new-password/<uidb64>/<token>/",
        UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("register/", UserRegisterView.as_view(), name="register"),
    path(
        "email-confirmation-sent/",
        EmailConfirmationSentView.as_view(),
        name="email_confirmation_sent",
    ),
    path(
        "confirm-email/<str:uidb64>/<str:token>/",
        UserConfirmEmailView.as_view(),
        name="confirm_email",
    ),
    path(
        "email-confirmed/",
        EmailConfirmedView.as_view(),
        name="email_confirmed",  # noqa: E501
    ),  # noqa: E501
    path(
        "confirm-email-failed/",
        EmailConfirmationFailedView.as_view(),
        name="email_confirmation_failed",
    ),
    path("feedback/", FeedbackCreateView.as_view(), name="feedback"),
]
