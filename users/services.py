from django.shortcuts import get_object_or_404

from appointments.models import Appointment
from treatments.models import Treatment

from .models import User


def get_managed_patient(doctor: User, patient_id: int) -> User:
    return get_object_or_404(
        User.objects.filter(role=User.Role.PATIENT, primary_doctor=doctor),
        pk=patient_id,
    )


def build_doctor_patient_context(patient: User) -> dict:
    treatment = Treatment.objects.filter(patient=patient, is_active=True).prefetch_related("steps").first()
    appointments = Appointment.objects.filter(patient=patient).order_by("scheduled_at")[:5]
    return {
        "patient": patient,
        "treatment": treatment,
        "current_step": treatment.current_step if treatment else None,
        "next_step": treatment.next_step if treatment else None,
        "appointments": appointments,
    }
