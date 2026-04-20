from django.urls import include, path


urlpatterns = [
    path("auth/", include("users.api_urls")),
    path("doctor/", include("users.doctor_api_urls")),
    path("", include("core.api_urls")),
    path("", include("treatments.api_urls")),
    path("", include("appointments.api_urls")),
    path("", include("medications.api_urls")),
    path("", include("assistant.api_urls")),
]
