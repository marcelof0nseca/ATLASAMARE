from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from core.mixins import PatientOrPartnerRequiredMixin
from core.services import group_medications_for_patient

from .models import Medication
from .services import complete_medication_dose


class MedicationListView(PatientOrPartnerRequiredMixin, TemplateView):
    template_name = "patient/medications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.request.user.linked_patient if self.request.user.is_partner else self.request.user
        context.update(group_medications_for_patient(patient))
        context["active_nav"] = "routine"
        return context


class MedicationConfirmView(PatientOrPartnerRequiredMixin, View):
    def get(self, request, pk):
        patient = request.user.linked_patient if request.user.is_partner else request.user
        medication = get_object_or_404(Medication, pk=pk, patient=patient)
        return render(request, "patient/partials/medication_confirm.html", {"medication": medication})


class MedicationCompleteView(PatientOrPartnerRequiredMixin, View):
    def post(self, request, pk):
        patient = request.user.linked_patient if request.user.is_partner else request.user
        medication = get_object_or_404(Medication, pk=pk, patient=patient)
        completed = False
        try:
            complete_medication_dose(medication=medication, actor=request.user)
            completed = True
            trigger = '{"showToast":{"message":"Tudo certo, medicação marcada.","tone":"success"},"closeModal":true}'
        except (ValidationError, PermissionDenied) as exc:
            trigger = '{"showToast":{"message":"Não foi possível marcar essa medicação agora.","tone":"error"},"closeModal":true}'
            messages.error(request, str(exc))

        if request.headers.get("HX-Request") == "true":
            response = HttpResponse(
                render_to_string(
                    "patient/partials/medication_row.html",
                    {"medication": medication},
                    request=request,
                )
            )
            response["HX-Trigger"] = trigger
            return response

        if completed:
            messages.success(request, "Tudo certo, medicação marcada.")
        if request.user.is_partner:
            return redirect("partner:routine")
        return redirect("medications:list")

# Create your views here.
