from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Max
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from core.mixins import (
    DoctorRequiredMixin,
    PartnerRequiredMixin,
    PatientOrPartnerRequiredMixin,
    PatientRequiredMixin,
)
from core.services import get_current_report

from .forms import JourneyDocumentForm, JourneyVideoForm
from .models import JourneyDocument, JourneyVideo, Treatment, TreatmentStep
from .services import complete_treatment_step, start_treatment_step


def get_active_treatment(patient):
    return Treatment.objects.filter(
        patient=patient,
        is_active=True,
    ).prefetch_related("steps").first()


def build_document_weeks(treatment, week_url_name):
    if not treatment:
        return [
            {"number": number, "unlocked": False, "url": ""}
            for number in range(1, 6)
        ]

    steps = list(treatment.steps.all())
    max_step = max([step.order for step in steps], default=0)
    max_document = treatment.documents.aggregate(max_week=Max("week"))["max_week"] or 0
    total_weeks = max(max_step, max_document, 5)
    unlocked_weeks = {
        step.order
        for step in steps
        if step.status in {TreatmentStep.Status.COMPLETED, TreatmentStep.Status.IN_PROGRESS}
    }
    return [
        {
            "number": number,
            "unlocked": number in unlocked_weeks,
            "url": reverse(week_url_name, args=[number]) if number in unlocked_weeks else "",
        }
        for number in range(1, total_weeks + 1)
    ]


def user_patient(user):
    return user.linked_patient if user.is_partner else user


def build_video_steps(videos):
    grouped = {}
    for video in videos:
        grouped.setdefault(video.step, []).append(video)
    max_step = max(grouped.keys(), default=10)
    return [
        {"number": number, "videos": grouped.get(number, [])}
        for number in range(1, max(max_step, 10) + 1)
    ]


class PatientTreatmentTimelineView(PatientRequiredMixin, TemplateView):
    template_name = "patient/treatment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        treatment = get_active_treatment(self.request.user)
        context.update(
            {
                "treatment": treatment,
                "active_nav": "treatment",
                "current_step": treatment.current_step if treatment else None,
                "next_step": treatment.next_step if treatment else None,
                "report": get_current_report(self.request.user),
            }
        )
        return context


class PatientJourneyDocumentsView(PatientRequiredMixin, TemplateView):
    template_name = "treatments/documents.html"
    week_url_name = "treatments:documents-week"

    def get_context_data(self, **kwargs):
        treatment = get_active_treatment(self.request.user)
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "active_nav": "documents",
                "treatment": treatment,
                "weeks": build_document_weeks(treatment, self.week_url_name),
                "back_url": reverse("treatments:timeline"),
                "is_partner_mode": False,
                "base_template": "layouts/patient_base.html",
            }
        )
        return context


class PatientJourneyWeekDocumentsView(PatientRequiredMixin, TemplateView):
    template_name = "treatments/week_documents.html"
    documents_url_name = "treatments:documents"

    def get(self, request, *args, **kwargs):
        treatment = get_active_treatment(request.user)
        week = kwargs["week"]
        weeks = build_document_weeks(treatment, "treatments:documents-week")
        selected_week = next((item for item in weeks if item["number"] == week), None)
        if not selected_week or not selected_week["unlocked"]:
            messages.info(request, "Documentos ainda não disponíveis.")
            return redirect(self.documents_url_name)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        treatment = get_active_treatment(self.request.user)
        week = self.kwargs["week"]
        documents = JourneyDocument.objects.filter(treatment=treatment, week=week)
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "active_nav": "documents",
                "week": week,
                "documents": documents,
                "documents_url": reverse(self.documents_url_name),
                "is_partner_mode": False,
                "base_template": "layouts/patient_base.html",
            }
        )
        return context


class PartnerJourneyDocumentsView(PartnerRequiredMixin, TemplateView):
    template_name = "treatments/documents.html"
    week_url_name = "treatments:partner-documents-week"

    def get_context_data(self, **kwargs):
        patient = self.request.user.linked_patient
        treatment = get_active_treatment(patient)
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "active_nav": "treatment",
                "treatment": treatment,
                "linked_patient": patient,
                "weeks": build_document_weeks(treatment, self.week_url_name),
                "back_url": reverse("partner:treatment"),
                "is_partner_mode": True,
                "base_template": "layouts/partner_base.html",
            }
        )
        return context


class PartnerJourneyWeekDocumentsView(PartnerRequiredMixin, TemplateView):
    template_name = "treatments/week_documents.html"
    documents_url_name = "treatments:partner-documents"

    def get(self, request, *args, **kwargs):
        patient = request.user.linked_patient
        treatment = get_active_treatment(patient)
        week = kwargs["week"]
        weeks = build_document_weeks(treatment, "treatments:partner-documents-week")
        selected_week = next((item for item in weeks if item["number"] == week), None)
        if not selected_week or not selected_week["unlocked"]:
            messages.info(request, "Documentos ainda não disponíveis.")
            return redirect(self.documents_url_name)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        patient = self.request.user.linked_patient
        treatment = get_active_treatment(patient)
        week = self.kwargs["week"]
        documents = JourneyDocument.objects.filter(treatment=treatment, week=week)
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "active_nav": "treatment",
                "linked_patient": patient,
                "week": week,
                "documents": documents,
                "documents_url": reverse(self.documents_url_name),
                "is_partner_mode": True,
                "base_template": "layouts/partner_base.html",
            }
        )
        return context


class JourneyDocumentDownloadView(PatientOrPartnerRequiredMixin, View):
    def get(self, request, pk):
        patient = user_patient(request.user)
        document = get_object_or_404(
            JourneyDocument.objects.select_related("treatment"),
            pk=pk,
            treatment__patient=patient,
        )
        unlocked_weeks = build_document_weeks(document.treatment, "treatments:documents-week")
        selected_week = next((item for item in unlocked_weeks if item["number"] == document.week), None)
        if not selected_week or not selected_week["unlocked"]:
            raise Http404("Documento indisponível")
        if not document.file:
            raise Http404("Arquivo indisponível")

        response = FileResponse(document.file.open("rb"), as_attachment=False, filename=document.original_name)
        response["Content-Disposition"] = f'inline; filename="{document.original_name}"'
        return response


class PatientJourneyVideoListView(PatientRequiredMixin, TemplateView):
    template_name = "treatments/videos.html"

    def get_context_data(self, **kwargs):
        videos = JourneyVideo.objects.filter(is_active=True)
        selected_step = self.request.GET.get("step", "").strip()
        if selected_step.isdigit():
            videos = videos.filter(step=int(selected_step))
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "active_nav": "videos",
                "videos": videos,
                "video_steps": build_video_steps(list(JourneyVideo.objects.filter(is_active=True))),
                "selected_step": selected_step,
            }
        )
        return context


class PatientJourneyVideoDetailView(PatientRequiredMixin, TemplateView):
    template_name = "treatments/video_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "active_nav": "videos",
                "video": get_object_or_404(JourneyVideo, pk=self.kwargs["pk"], is_active=True),
            }
        )
        return context


class DoctorJourneyVideoListView(DoctorRequiredMixin, ListView):
    template_name = "doctor/journey_videos.html"
    model = JourneyVideo
    context_object_name = "videos"

    def get_queryset(self):
        return JourneyVideo.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "videos"
        return context


class DoctorJourneyVideoCreateView(DoctorRequiredMixin, CreateView):
    template_name = "doctor/journey_video_form.html"
    form_class = JourneyVideoForm
    success_url = reverse_lazy("treatments:doctor-videos")

    def form_valid(self, form):
        messages.success(self.request, "Vídeo da jornada cadastrado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "videos"
        context["form_title"] = "Novo vídeo"
        return context


class DoctorJourneyVideoUpdateView(DoctorRequiredMixin, UpdateView):
    template_name = "doctor/journey_video_form.html"
    model = JourneyVideo
    form_class = JourneyVideoForm
    success_url = reverse_lazy("treatments:doctor-videos")

    def form_valid(self, form):
        messages.success(self.request, "Vídeo da jornada atualizado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "videos"
        context["form_title"] = "Editar vídeo"
        return context


class DoctorJourneyVideoDeleteView(DoctorRequiredMixin, DeleteView):
    model = JourneyVideo
    success_url = reverse_lazy("treatments:doctor-videos")

    def post(self, request, *args, **kwargs):
        messages.success(request, "Vídeo removido da jornada.")
        return super().post(request, *args, **kwargs)


class DoctorJourneyVideoToggleView(DoctorRequiredMixin, View):
    def post(self, request, pk):
        video = get_object_or_404(JourneyVideo, pk=pk)
        video.is_active = not video.is_active
        video.save(update_fields=["is_active", "updated_at"])
        status = "ativado" if video.is_active else "desativado"
        messages.success(request, f"Vídeo {status}.")
        return redirect("treatments:doctor-videos")


class DoctorJourneyDocumentListView(DoctorRequiredMixin, ListView):
    template_name = "doctor/journey_documents.html"
    model = JourneyDocument
    context_object_name = "documents"

    def get_queryset(self):
        return JourneyDocument.objects.select_related("treatment__patient").filter(
            treatment__patient__primary_doctor=self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "documents"
        return context


class DoctorJourneyDocumentCreateView(DoctorRequiredMixin, CreateView):
    template_name = "doctor/journey_document_form.html"
    form_class = JourneyDocumentForm
    success_url = reverse_lazy("treatments:doctor-documents")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["doctor"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Documento da jornada cadastrado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "documents"
        context["form_title"] = "Novo documento"
        return context


class DoctorJourneyDocumentUpdateView(DoctorRequiredMixin, UpdateView):
    template_name = "doctor/journey_document_form.html"
    form_class = JourneyDocumentForm
    success_url = reverse_lazy("treatments:doctor-documents")

    def get_queryset(self):
        return JourneyDocument.objects.filter(treatment__patient__primary_doctor=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["doctor"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Documento da jornada atualizado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_nav"] = "documents"
        context["form_title"] = "Editar documento"
        return context


class DoctorJourneyDocumentDeleteView(DoctorRequiredMixin, DeleteView):
    success_url = reverse_lazy("treatments:doctor-documents")

    def get_queryset(self):
        return JourneyDocument.objects.filter(treatment__patient__primary_doctor=self.request.user)

    def post(self, request, *args, **kwargs):
        messages.success(request, "Documento removido da jornada.")
        return super().post(request, *args, **kwargs)


class DoctorStartTreatmentStepView(DoctorRequiredMixin, View):
    def post(self, request, treatment_id, step_id):
        step = get_object_or_404(
            TreatmentStep.objects.select_related("treatment__patient"),
            pk=step_id,
            treatment_id=treatment_id,
        )
        try:
            start_treatment_step(step=step, actor=request.user)
            messages.success(request, "Etapa iniciada com clareza. A paciente já vê esse avanço.")
        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, str(exc))
        return redirect("users:doctor-patient-detail", pk=step.treatment.patient_id)


class DoctorCompleteTreatmentStepView(DoctorRequiredMixin, View):
    def post(self, request, treatment_id, step_id):
        step = get_object_or_404(
            TreatmentStep.objects.select_related("treatment__patient"),
            pk=step_id,
            treatment_id=treatment_id,
        )
        try:
            complete_treatment_step(step=step, actor=request.user)
            messages.success(request, "Etapa concluída. O próximo passo já foi organizado.")
        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, str(exc))
        return redirect("users:doctor-patient-detail", pk=step.treatment.patient_id)

# Create your views here.
