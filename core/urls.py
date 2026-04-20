from django.urls import path

from .views import PatientDashboardView, RootRedirectView


app_name = "core"

urlpatterns = [
    path("", RootRedirectView.as_view(), name="root"),
    path("dashboard/", PatientDashboardView.as_view(), name="dashboard"),
]
