from django.views.generic import TemplateView

from core.mixins import PatientRequiredMixin
from core.services import group_appointments_by_date

from .models import Appointment


class AppointmentListView(PatientRequiredMixin, TemplateView):
    template_name = "patient/appointments.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointments = Appointment.objects.filter(patient=self.request.user).order_by("scheduled_at")
        context["appointments_by_date"] = group_appointments_by_date(appointments)
        context["active_nav"] = "routine"
        return context

# Create your views here.
