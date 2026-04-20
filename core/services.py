from collections import defaultdict

from django.utils import timezone

from appointments.models import Appointment
from medications.models import Medication
from treatments.models import Treatment


def build_patient_dashboard(user):
    today = timezone.localdate()
    treatment = Treatment.objects.filter(patient=user, is_active=True).prefetch_related("steps").first()
    appointments = Appointment.objects.filter(
        patient=user, scheduled_at__date__gte=today
    ).order_by("scheduled_at")[:3]
    medications_today = Medication.objects.filter(
        patient=user,
        scheduled_for__date=today,
    ).order_by("scheduled_for")
    next_medication = medications_today.filter(status=Medication.Status.PENDING).first()

    return {
        "treatment": treatment,
        "current_step": treatment.current_step if treatment else None,
        "next_step": treatment.next_step if treatment else None,
        "appointments": appointments,
        "medications_today": medications_today,
        "next_medication": next_medication,
    }


def group_appointments_by_date(queryset):
    grouped = defaultdict(list)
    for appointment in queryset:
        grouped[timezone.localtime(appointment.scheduled_at).date()].append(appointment)
    return dict(grouped)


def group_medications_for_patient(user):
    now = timezone.localtime()
    today = now.date()
    queryset = Medication.objects.filter(patient=user).order_by("scheduled_for")
    return {
        "now_items": queryset.filter(scheduled_for__date=today, status=Medication.Status.PENDING)[:2],
        "today_items": queryset.filter(scheduled_for__date=today),
        "upcoming_items": queryset.filter(scheduled_for__date__gt=today)[:5],
    }
