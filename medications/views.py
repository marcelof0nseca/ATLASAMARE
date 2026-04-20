from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from core.mixins import PatientRequiredMixin
from core.services import group_medications_for_patient

from .models import Medication
from .services import complete_medication_dose


class MedicationListView(PatientRequiredMixin, TemplateView):
    template_name = "patient/medications.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(group_medications_for_patient(self.request.user))
        context["active_nav"] = "routine"
        return context


class MedicationConfirmView(PatientRequiredMixin, View):
    def get(self, request, pk):
        medication = get_object_or_404(Medication, pk=pk, patient=request.user)
        return render(request, "patient/partials/medication_confirm.html", {"medication": medication})


class MedicationCompleteView(PatientRequiredMixin, View):
    def post(self, request, pk):
        medication = get_object_or_404(Medication, pk=pk, patient=request.user)
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
        return redirect("medications:list")

# Create your views here.
