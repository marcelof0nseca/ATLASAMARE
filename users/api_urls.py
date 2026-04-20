from django.urls import path

from .api_views import (
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    PasswordResetRequestAPIView,
)


urlpatterns = [
    path("login", LoginAPIView.as_view(), name="api-login"),
    path("logout", LogoutAPIView.as_view(), name="api-logout"),
    path("me", MeAPIView.as_view(), name="api-me"),
    path("password-reset-request", PasswordResetRequestAPIView.as_view(), name="api-password-reset"),
]
