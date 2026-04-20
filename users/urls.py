from django.urls import path

from .views import (
    DoctorPatientDetailView,
    DoctorPatientListView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    ProfileView,
)


app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("forgot-access/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("doctor/patients/", DoctorPatientListView.as_view(), name="doctor-patient-list"),
    path("doctor/patients/<int:pk>/", DoctorPatientDetailView.as_view(), name="doctor-patient-detail"),
]
