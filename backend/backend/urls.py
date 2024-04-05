# pylint: disable=invalid-name
"""URL configuration for backend project."""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

handler403 = "modules.system.views.tr_handler403"
handler404 = "modules.system.views.tr_handler404"
handler500 = "modules.system.views.tr_handler500"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("", include("modules.companies.urls")),
    path("", include("modules.applications.urls")),
    path("", include("modules.system.urls")),
]

if settings.DEBUG:
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls"))
    ] + urlpatterns  # noqa: E501
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )  # noqa: E501
