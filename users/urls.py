from django.urls import path

from .views import (
    ChangePasswordView,
    DoctorPatientCreateView,
    DoctorPatientDetailView,
    DoctorPatientListView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    ProfileSectionView,
    ProfileView,
)


app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("forgot-access/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/<str:section>/", ProfileSectionView.as_view(), name="profile-update"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("doctor/patients/", DoctorPatientListView.as_view(), name="doctor-patient-list"),
    path("doctor/patients/new/", DoctorPatientCreateView.as_view(), name="doctor-patient-create"),
    path("doctor/patients/<int:pk>/", DoctorPatientDetailView.as_view(), name="doctor-patient-detail"),
]
