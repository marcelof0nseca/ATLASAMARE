from django.views.generic import TemplateView
from django.utils import timezone

from core.mixins import PatientRequiredMixin
from core.services import build_routine_calendar, group_appointments_by_date

from .models import Appointment


class AppointmentListView(PatientRequiredMixin, TemplateView):
    template_name = "patient/appointments.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointments = Appointment.objects.filter(patient=self.request.user).order_by("scheduled_at")
        upcoming_appointments = appointments.filter(scheduled_at__date__gte=timezone.localdate())
        context["appointments_by_date"] = group_appointments_by_date(appointments)
        context["routine_calendar"] = build_routine_calendar(timezone.localdate(), upcoming_appointments, [], [])
        context["upcoming_appointments"] = upcoming_appointments[:4]
        context["active_nav"] = "routine"
        return context

# Create your views here.
