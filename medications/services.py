from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from .models import Medication


def complete_medication_dose(medication: Medication, actor) -> Medication:
    is_authorized = False
    if actor.is_patient and medication.patient_id == actor.id:
        is_authorized = True
    elif actor.is_partner and medication.patient_id == actor.linked_patient_id:
        is_authorized = True

    if not is_authorized:
        raise PermissionDenied("Você não tem permissão para marcar esta medicação.")
    if medication.status == Medication.Status.COMPLETED:
        raise ValidationError("Essa dose já foi marcada.")
    medication.status = Medication.Status.COMPLETED
    medication.completed_at = timezone.now()
    medication.save(update_fields=["status", "completed_at"])
    return medication
