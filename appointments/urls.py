from django.urls import path

from .views import AppointmentListView


app_name = "appointments"

urlpatterns = [
    path("routine/appointments/", AppointmentListView.as_view(), name="list"),
]
