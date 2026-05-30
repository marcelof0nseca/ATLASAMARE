from django.urls import path
from .partner_views import (
    PartnerDashboardView, PartnerTreatmentView, PartnerRoutineView,
    PartnerMayaView, PartnerMayaSendView, PartnerProfileView,
)

app_name = "partner"

urlpatterns = [
    path("partner/dashboard/", PartnerDashboardView.as_view(), name="dashboard"),
    path("partner/treatment/", PartnerTreatmentView.as_view(), name="treatment"),
    path("partner/routine/", PartnerRoutineView.as_view(), name="routine"),
    path("partner/maya/", PartnerMayaView.as_view(), name="maya"),
    path("partner/maya/send/", PartnerMayaSendView.as_view(), name="maya-send"),
    path("partner/maya/<slug:conversation_kind>/", PartnerMayaView.as_view(), name="maya-kind"),
    path("partner/profile/", PartnerProfileView.as_view(), name="profile"),
]
