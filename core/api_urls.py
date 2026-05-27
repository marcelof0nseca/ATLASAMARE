from django.urls import path

from .api_views import (
    CommunityPostListCreateAPIView,
    CommunityReactionAPIView,
    CurrentReportAPIView,
    DashboardAPIView,
    PartnerListAPIView,
    PatientTaskListCreateAPIView,
)


urlpatterns = [
    path("dashboard", DashboardAPIView.as_view(), name="api-dashboard"),
    path("routine/tasks", PatientTaskListCreateAPIView.as_view(), name="api-routine-tasks"),
    path("partners", PartnerListAPIView.as_view(), name="api-partners"),
    path("community/posts", CommunityPostListCreateAPIView.as_view(), name="api-community-posts"),
    path("community/posts/<int:pk>/react", CommunityReactionAPIView.as_view(), name="api-community-react"),
    path("reports/current", CurrentReportAPIView.as_view(), name="api-current-report"),
]
