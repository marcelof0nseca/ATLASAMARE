from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from core.mixins import DoctorRequiredMixin, PatientRequiredMixin

from .models import Treatment, TreatmentStep
from .services import complete_treatment_step, start_treatment_step


class PatientTreatmentTimelineView(PatientRequiredMixin, TemplateView):
    template_name = "patient/treatment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        treatment = Treatment.objects.filter(
            patient=self.request.user,
            is_active=True,
        ).prefetch_related("steps").first()
        context.update(
            {
                "treatment": treatment,
                "active_nav": "treatment",
                "current_step": treatment.current_step if treatment else None,
                "next_step": treatment.next_step if treatment else None,
            }
        )
        return context


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
