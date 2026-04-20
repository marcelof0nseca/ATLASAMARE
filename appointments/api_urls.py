from django.urls import path

from .api_views import AppointmentListAPIView


urlpatterns = [
    path("appointments", AppointmentListAPIView.as_view(), name="api-appointments"),
]
