from django.urls import path

from .views import MedicationCompleteView, MedicationConfirmView, MedicationListView


app_name = "medications"

urlpatterns = [
    path("routine/medications/", MedicationListView.as_view(), name="list"),
    path("routine/medications/<int:pk>/confirm/", MedicationConfirmView.as_view(), name="confirm"),
    path("routine/medications/<int:pk>/complete/", MedicationCompleteView.as_view(), name="complete"),
]
