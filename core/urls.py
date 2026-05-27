from django.urls import path

from .views import LandingView, PatientDashboardView, RootRedirectView


app_name = "core"

urlpatterns = [
    path("", RootRedirectView.as_view(), name="root"),
    path("landing/", LandingView.as_view(), name="landing"),
    path("dashboard/", PatientDashboardView.as_view(), name="dashboard"),
]
