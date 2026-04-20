from django.urls import path

from .api_views import (
    CompleteTreatmentStepAPIView,
    CurrentTreatmentAPIView,
    StartTreatmentStepAPIView,
)


urlpatterns = [
    path("treatments/current", CurrentTreatmentAPIView.as_view(), name="api-current-treatment"),
    path(
        "doctor/treatments/<int:treatment_id>/steps/<int:step_id>/start",
        StartTreatmentStepAPIView.as_view(),
        name="api-doctor-step-start",
    ),
    path(
        "doctor/treatments/<int:treatment_id>/steps/<int:step_id>/complete",
        CompleteTreatmentStepAPIView.as_view(),
        name="api-doctor-step-complete",
    ),
]
