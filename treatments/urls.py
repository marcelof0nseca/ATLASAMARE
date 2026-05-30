from django.urls import path

from .views import (
    DoctorCompleteTreatmentStepView,
    DoctorJourneyDocumentCreateView,
    DoctorJourneyDocumentDeleteView,
    DoctorJourneyDocumentListView,
    DoctorJourneyDocumentUpdateView,
    DoctorJourneyVideoCreateView,
    DoctorJourneyVideoDeleteView,
    DoctorJourneyVideoListView,
    DoctorJourneyVideoToggleView,
    DoctorJourneyVideoUpdateView,
    DoctorStartTreatmentStepView,
    JourneyDocumentDownloadView,
    PartnerJourneyDocumentsView,
    PartnerJourneyWeekDocumentsView,
    PatientJourneyDocumentsView,
    PatientJourneyVideoDetailView,
    PatientJourneyVideoListView,
    PatientJourneyWeekDocumentsView,
    PatientTreatmentTimelineView,
)


app_name = "treatments"

urlpatterns = [
    path("treatment/", PatientTreatmentTimelineView.as_view(), name="timeline"),
    path("jornada/documentos/", PatientJourneyDocumentsView.as_view(), name="documents"),
    path("jornada/documentos/semana/<int:week>/", PatientJourneyWeekDocumentsView.as_view(), name="documents-week"),
    path("jornada/videos/", PatientJourneyVideoListView.as_view(), name="videos"),
    path("jornada/videos/<uuid:pk>/", PatientJourneyVideoDetailView.as_view(), name="video-detail"),
    path("partner/jornada/documentos/", PartnerJourneyDocumentsView.as_view(), name="partner-documents"),
    path(
        "partner/jornada/documentos/semana/<int:week>/",
        PartnerJourneyWeekDocumentsView.as_view(),
        name="partner-documents-week",
    ),
    path("jornada/documentos/<uuid:pk>/download/", JourneyDocumentDownloadView.as_view(), name="documents-download"),
    path("admin/jornada/videos/", DoctorJourneyVideoListView.as_view(), name="doctor-videos-admin"),
    path("doctor/jornada/videos/", DoctorJourneyVideoListView.as_view(), name="doctor-videos"),
    path("doctor/jornada/videos/new/", DoctorJourneyVideoCreateView.as_view(), name="doctor-video-create"),
    path("doctor/jornada/videos/<uuid:pk>/edit/", DoctorJourneyVideoUpdateView.as_view(), name="doctor-video-edit"),
    path("doctor/jornada/videos/<uuid:pk>/delete/", DoctorJourneyVideoDeleteView.as_view(), name="doctor-video-delete"),
    path("doctor/jornada/videos/<uuid:pk>/toggle/", DoctorJourneyVideoToggleView.as_view(), name="doctor-video-toggle"),
    path("admin/jornada/documentos/", DoctorJourneyDocumentListView.as_view(), name="doctor-documents-admin"),
    path("doctor/jornada/documentos/", DoctorJourneyDocumentListView.as_view(), name="doctor-documents"),
    path("doctor/jornada/documentos/new/", DoctorJourneyDocumentCreateView.as_view(), name="doctor-document-create"),
    path("doctor/jornada/documentos/<uuid:pk>/edit/", DoctorJourneyDocumentUpdateView.as_view(), name="doctor-document-edit"),
    path("doctor/jornada/documentos/<uuid:pk>/delete/", DoctorJourneyDocumentDeleteView.as_view(), name="doctor-document-delete"),
    path(
        "doctor/treatments/<int:treatment_id>/steps/<int:step_id>/start/",
        DoctorStartTreatmentStepView.as_view(),
        name="doctor-step-start",
    ),
    path(
        "doctor/treatments/<int:treatment_id>/steps/<int:step_id>/complete/",
        DoctorCompleteTreatmentStepView.as_view(),
        name="doctor-step-complete",
    ),
]
