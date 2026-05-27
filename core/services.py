from collections import defaultdict

from django.utils import timezone

from appointments.models import Appointment
from medications.models import Medication
from treatments.models import Treatment

from .models import CommunityPost, PatientTask, TreatmentReport


def build_patient_dashboard(user):
    today = timezone.localdate()
    treatment = Treatment.objects.filter(patient=user, is_active=True).prefetch_related("steps").first()
    appointments = Appointment.objects.filter(
        patient=user, scheduled_at__date__gte=today
    ).order_by("scheduled_at")[:3]

    # Uma única query para as medicações de hoje; filtragem da próxima dose em Python.
    medications_today = list(
        Medication.objects.filter(
            patient=user,
            scheduled_for__date=today,
        ).order_by("scheduled_for")
    )
    next_medication = next(
        (m for m in medications_today if m.status == Medication.Status.PENDING),
        None,
    )

    return {
        "treatment": treatment,
        "current_step": treatment.current_step if treatment else None,
        "next_step": treatment.next_step if treatment else None,
        "appointments": appointments,
        "medications_today": medications_today,
        "next_medication": next_medication,
        "next_appointment": appointments[0] if appointments else None,
        "pending_tasks_count": PatientTask.objects.filter(patient=user, status=PatientTask.Status.PENDING).count(),
        "report": get_current_report(user),
        # featured_posts e featured_partners removidos: não são usados no template do dashboard.
    }


def group_appointments_by_date(queryset):
    grouped = defaultdict(list)
    for appointment in queryset:
        grouped[timezone.localtime(appointment.scheduled_at).date()].append(appointment)
    return dict(grouped)


def group_medications_for_patient(user):
    today = timezone.localdate()

    # Uma única query traz hoje + próximas doses; filtragem feita em Python.
    all_meds = list(
        Medication.objects.filter(
            patient=user,
            scheduled_for__date__gte=today,
        ).order_by("scheduled_for")
    )

    now_item = next(
        (m for m in all_meds if m.scheduled_for.date() == today and m.status == Medication.Status.PENDING),
        None,
    )
    today_items = [
        m for m in all_meds
        if m.scheduled_for.date() == today and (now_item is None or m.pk != now_item.pk)
    ]
    upcoming_items = [m for m in all_meds if m.scheduled_for.date() > today][:5]

    return {
        "now_item": now_item,
        "today_items": today_items,
        "upcoming_items": upcoming_items,
    }


def get_current_report(user):
    return TreatmentReport.objects.filter(patient=user).order_by("-created_at").first()


def build_patient_routine(user):
    today = timezone.localdate()
    medications = group_medications_for_patient(user)

    # Filtra apenas compromissos a partir de hoje para não carregar todo o histórico.
    appointments = Appointment.objects.filter(
        patient=user,
        scheduled_at__date__gte=today,
    ).order_by("scheduled_at")

    tasks = PatientTask.objects.filter(patient=user).order_by("status", "due_at", "-created_at")
    return {
        **medications,
        "appointments_by_date": group_appointments_by_date(appointments),
        "tasks": tasks,
        "today_tasks": tasks.filter(due_at__date=today) | tasks.filter(due_at__isnull=True, status=PatientTask.Status.PENDING),
        "upcoming_appointments": appointments[:4],
    }


def get_explore_context(user):
    return {
        "approved_posts": CommunityPost.objects.filter(status=CommunityPost.Status.APPROVED)[:3],
        "featured_partners": Partner.objects.filter(is_active=True, is_featured=True)[:4],
        "pending_posts_count": CommunityPost.objects.filter(author=user, status=CommunityPost.Status.PENDING).count(),
    }
