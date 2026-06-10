from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, UpdateView

from appointments.models import Appointment
from assistant.services import (
    answer_question_with_maya,
    ensure_default_conversations,
    get_conversation_empty_state,
    get_conversation_or_default,
)
from core.mixins import PartnerRequiredMixin
from core.models import PatientTask
from core.services import (
    build_patient_dashboard,
    get_current_report,
    group_appointments_by_date,
    group_medications_for_patient,
)
from medications.models import Medication
from treatments.models import Treatment
from users.forms import ProfileForm


class PartnerDashboardView(PartnerRequiredMixin, TemplateView):
    template_name = "partner/dashboard.html"

    def get_context_data(self, **kwargs):
        patient = self.request.user.linked_patient
        context = super().get_context_data(**kwargs)
        context.update(build_patient_dashboard(patient))
        context["linked_patient"] = patient
        context["active_nav"] = "partner"
        return context


class PartnerTreatmentView(PartnerRequiredMixin, TemplateView):
    template_name = "partner/treatment.html"

    def get_context_data(self, **kwargs):
        patient = self.request.user.linked_patient
        treatment = Treatment.objects.filter(patient=patient, is_active=True).prefetch_related("steps").first()
        steps = treatment.steps.all() if treatment else []
        completed = [s for s in steps if s.status == "completed"]
        total = len(list(steps))
        percent = round(len(completed) / total * 100) if total > 0 else 0
        context = super().get_context_data(**kwargs)
        context.update({
            "treatment": treatment,
            "linked_patient": patient,
            "active_nav": "treatment",
            "current_step": treatment.current_step if treatment else None,
            "next_step": treatment.next_step if treatment else None,
            "completed_count": len(completed),
            "total_count": total,
            "progress_percent": percent,
            "report": get_current_report(patient),
        })
        return context


class PartnerRoutineView(PartnerRequiredMixin, TemplateView):
    template_name = "partner/routine.html"

    def get_context_data(self, **kwargs):
        patient = self.request.user.linked_patient
        context = super().get_context_data(**kwargs)
        meds_context = group_medications_for_patient(patient)
        
        # Format now_items as a list to prevent iteration mismatch in the template
        context["now_items"] = [meds_context["now_item"]] if meds_context.get("now_item") else []
        context["today_items"] = meds_context.get("today_items", [])
        
        context["appointments_by_date"] = group_appointments_by_date(
            Appointment.objects.filter(patient=patient).order_by("scheduled_at")
        )
        context["injection_items"] = []  # future model
        context["expected_symptoms"] = []  # future model
        context["linked_patient"] = patient
        context["active_nav"] = "routine"
        context["tabs"] = [
            ("medicamentos", "Medicamentos"),
            ("consultas", "Consultas"),
            ("sintomas", "Diário de Sintomas"),
            ("lembretes", "Lembretes"),
            ("injecoes", "Injeções"),
            ("recordacoes", "Recordações"),
        ]
        return context

    def post(self, request, *args, **kwargs):
        patient = request.user.linked_patient
        unexpected_symptoms = request.POST.get("unexpected_symptoms", "").strip()
        if unexpected_symptoms:
            PatientTask.objects.create(
                patient=patient,
                title="Sintoma inesperado registrado pelo acompanhante",
                notes=unexpected_symptoms[:220],
                due_at=timezone.now(),
            )
            messages.success(request, f"Sintoma inesperado registrado com sucesso na rotina de {patient.preferred_name}.")
        else:
            messages.error(request, "A descrição do sintoma não pode estar vazia.")
        return redirect("partner:routine")


class PartnerMayaView(PartnerRequiredMixin, TemplateView):
    template_name = "partner/maya.html"

    def get_context_data(self, **kwargs):
        conversations = ensure_default_conversations(self.request.user)
        selected = get_conversation_or_default(
            self.request.user, self.kwargs.get("conversation_kind")
        )
        recent = list(selected.interactions.order_by("-created_at")[:12])[::-1]
        patient = self.request.user.linked_patient
        context = super().get_context_data(**kwargs)
        
        # Custom examples tailored for partner user
        partner_examples = {
            "treatment": [
                f"Como posso apoiar {patient.preferred_name} na etapa atual?",
                "O que acontece depois dessa fase do tratamento?",
                "Quais cuidados ela precisa ter agora?",
            ],
            "routine": [
                f"Como posso ajudar com as medicações de {patient.preferred_name}?",
                "O que devo fazer quando ela se esquecer de um remédio?",
                "Como organizar a rotina dela nesta semana?",
            ],
            "feelings": [
                "O que devo fazer quando ela estiver ansiosa?",
                "Como ofereço apoio sem ser invasivo?",
                "Estou me sentindo impotente. O que posso fazer?",
            ],
        }
        examples = partner_examples.get(selected.kind, [
            f"Como posso apoiar {patient.preferred_name}?",
            "Como ajudo com a rotina?",
            "Como ajudar nos sentimentos?",
        ])

        context.update({
            "conversations": conversations,
            "selected_conversation": selected,
            "interactions": recent,
            "empty_state": get_conversation_empty_state(selected.kind),
            "linked_patient": patient,
            "active_nav": "maya",
            "prompt_examples": examples,
        })
        return context


class PartnerMayaSendView(PartnerRequiredMixin, View):
    def post(self, request):
        question = request.POST.get("question", "").strip()
        conversation = get_conversation_or_default(
            request.user,
            request.POST.get("conversation_kind"),
        )
        try:
            interaction = answer_question_with_maya(
                user=request.user,
                question=question,
                conversation=conversation,
            )
        except ValidationError as exc:
            if request.headers.get("HX-Request") == "true":
                return render(
                    request,
                    "patient/partials/maya_exchange.html",
                    {
                        "interaction": {
                            "question": question or "Pergunta vazia",
                            "answer": exc.message,
                            "intent": "general",
                            "risk_level": "low",
                            "suggested_next_step": "",
                        }
                    },
                    status=400,
                )
            messages.error(request, exc.message)
            return redirect("partner:maya-kind", conversation_kind=conversation.kind)

        if request.headers.get("HX-Request") == "true":
            return render(
                request,
                "patient/partials/maya_exchange.html",
                {"interaction": interaction},
            )

        messages.success(request, "A Maya respondeu com cuidado.")
        return redirect("partner:maya-kind", conversation_kind=conversation.kind)


class PartnerProfileView(PartnerRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "partner/profile.html"
    success_url = reverse_lazy("partner:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Suas preferências foram atualizadas com cuidado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["linked_patient"] = self.request.user.linked_patient
        context["active_nav"] = "profile"
        return context
