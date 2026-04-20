from django.urls import path

from .views import (
    DoctorCompleteTreatmentStepView,
    DoctorStartTreatmentStepView,
    PatientTreatmentTimelineView,
)


app_name = "treatments"

urlpatterns = [
    path("treatment/", PatientTreatmentTimelineView.as_view(), name="timeline"),
    path(
        "doctor/treatments/<int:treatment_id>/steps/<int:step_id>/start/",
        DoctorStartTreatmentStepView.as_view(),
        name="doctor-step-start",
    ),
    path(
        "doctor/treatments/<int:treatment_id>/steps/<int:step_id>/complete/",
        DoctorCompleteTreatmentStepView.as_view(),
        name="doctor-step-complete",
    ),
]
