from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import TreatmentStep


def _assert_managed_doctor(step: TreatmentStep, actor) -> None:
    if not actor.is_doctor:
        raise PermissionDenied("Apenas médicas responsáveis podem atualizar o tratamento.")
    if step.treatment.patient.primary_doctor_id != actor.id:
        raise PermissionDenied("Essa paciente não está sob responsabilidade desse médico.")


def _previous_steps_completed(step: TreatmentStep) -> bool:
    return not step.treatment.steps.filter(order__lt=step.order).exclude(
        status=TreatmentStep.Status.COMPLETED
    ).exists()


@transaction.atomic
def start_treatment_step(step: TreatmentStep, actor) -> TreatmentStep:
    _assert_managed_doctor(step, actor)
    if step.status != TreatmentStep.Status.PENDING:
        raise ValidationError("Somente etapas pendentes podem ser iniciadas.")
    if step.treatment.steps.filter(status=TreatmentStep.Status.IN_PROGRESS).exists():
        raise ValidationError("Já existe uma etapa em andamento nesse tratamento.")
    if not _previous_steps_completed(step):
        raise ValidationError("As etapas anteriores precisam estar concluídas antes de iniciar esta.")
    step.status = TreatmentStep.Status.IN_PROGRESS
    step.save(update_fields=["status", "updated_at"])
    return step


@transaction.atomic
def complete_treatment_step(step: TreatmentStep, actor) -> TreatmentStep:
    _assert_managed_doctor(step, actor)
    if step.status != TreatmentStep.Status.IN_PROGRESS:
        raise ValidationError("Apenas a etapa atual pode ser concluída.")

    step.status = TreatmentStep.Status.COMPLETED
    step.save(update_fields=["status", "updated_at"])

    next_step = step.treatment.steps.filter(
        order__gt=step.order,
        status=TreatmentStep.Status.PENDING,
    ).order_by("order").first()
    if next_step:
        next_step.status = TreatmentStep.Status.IN_PROGRESS
        next_step.save(update_fields=["status", "updated_at"])
    return step
