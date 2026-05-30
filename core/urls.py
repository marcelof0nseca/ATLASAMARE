from django.urls import path

from .views import (
    CommunityFeedView,
    CommunityPostCreateView,
    CommunityReactView,
    ExploreHomeView,
    LandingView,
    PartnerListView,
    PatientDashboardView,
    PatientRoutineView,
    PatientTaskCompleteView,
    PatientTaskCreateView,
    PatientTaskUpdateView,
    ReportDownloadView,
    RootRedirectView,
    SupportCommunityListView,
)


app_name = "core"

urlpatterns = [
    path("", RootRedirectView.as_view(), name="root"),
    path("landing/", LandingView.as_view(), name="landing"),
    path("dashboard/", PatientDashboardView.as_view(), name="dashboard"),
    path("routine/", PatientRoutineView.as_view(), name="routine"),
    path("routine/tasks/create/", PatientTaskCreateView.as_view(), name="task-create"),
    path("routine/tasks/<int:pk>/update/", PatientTaskUpdateView.as_view(), name="task-update"),
    path("routine/tasks/<int:pk>/complete/", PatientTaskCompleteView.as_view(), name="task-complete"),
    path("explore/", ExploreHomeView.as_view(), name="explore"),
    path("comunidades/", SupportCommunityListView.as_view(), name="communities"),
    path("explore/partners/", PartnerListView.as_view(), name="partners"),
    path("explore/community/", CommunityFeedView.as_view(), name="community"),
    path("explore/community/new/", CommunityPostCreateView.as_view(), name="community-create"),
    path("explore/community/<int:pk>/react/", CommunityReactView.as_view(), name="community-react"),
    path("reports/<int:pk>/download/", ReportDownloadView.as_view(), name="report-download"),
]
