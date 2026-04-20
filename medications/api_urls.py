from django.urls import path

from .api_views import MedicationCompleteAPIView, MedicationListAPIView


urlpatterns = [
    path("medications", MedicationListAPIView.as_view(), name="api-medications"),
    path("medications/<int:pk>/complete", MedicationCompleteAPIView.as_view(), name="api-medication-complete"),
]
