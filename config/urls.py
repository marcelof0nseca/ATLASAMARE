from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", include("users.urls")),
    path("", include("treatments.urls")),
    path("", include("appointments.urls")),
    path("", include("medications.urls")),
    path("", include("assistant.urls")),
    path("api/v1/", include("config.api_urls")),
]
