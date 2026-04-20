from django.urls import path

from .api_views import DoctorPatientDetailAPIView, DoctorPatientsAPIView


urlpatterns = [
    path("patients", DoctorPatientsAPIView.as_view(), name="api-doctor-patients"),
    path("patients/<int:pk>", DoctorPatientDetailAPIView.as_view(), name="api-doctor-patient-detail"),
]
