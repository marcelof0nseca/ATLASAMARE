from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone

from .models import Medication


def complete_medication_dose(medication: Medication, actor) -> Medication:
    if not actor.is_patient or medication.patient_id != actor.id:
        raise PermissionDenied("Você só pode marcar as próprias medicações.")
    if medication.status == Medication.Status.COMPLETED:
        raise ValidationError("Essa dose já foi marcada.")
    medication.status = Medication.Status.COMPLETED
    medication.completed_at = timezone.now()
    medication.save(update_fields=["status", "completed_at"])
    return medication
