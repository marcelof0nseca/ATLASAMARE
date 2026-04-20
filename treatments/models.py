from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class Treatment(models.Model):
    patient = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="treatments",
        limit_choices_to={"role": "patient"},
    )
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["patient"],
                condition=Q(is_active=True),
                name="unique_active_treatment_per_patient",
            )
        ]
        verbose_name = _("tratamento")
        verbose_name_plural = _("tratamentos")

    def __str__(self) -> str:
        return f"{self.name} - {self.patient.full_name}"

    def clean(self) -> None:
        super().clean()
        if not self.patient.is_patient:
            raise ValidationError({"patient": _("O tratamento deve estar vinculado a uma paciente.")})

    @property
    def current_step(self):
        return self.steps.filter(status=TreatmentStep.Status.IN_PROGRESS).order_by("order").first()

    @property
    def next_step(self):
        current_step = self.current_step
        if current_step:
            return self.steps.filter(order__gt=current_step.order).order_by("order").first()
        return self.steps.exclude(status=TreatmentStep.Status.COMPLETED).order_by("order").first()


class TreatmentStep(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pendente")
        IN_PROGRESS = "in_progress", _("Em andamento")
        COMPLETED = "completed", _("Concluído")

    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name="steps")
    name = models.CharField(max_length=120)
    order = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["treatment", "order"], name="unique_treatment_step_order"),
        ]
        verbose_name = _("etapa do tratamento")
        verbose_name_plural = _("etapas do tratamento")

    def __str__(self) -> str:
        return f"{self.order}. {self.name}"

    def clean(self) -> None:
        super().clean()
        if self.status == self.Status.IN_PROGRESS:
            previous_not_completed = self.treatment.steps.exclude(pk=self.pk).filter(
                order__lt=self.order
            ).exclude(status=self.Status.COMPLETED)
            if previous_not_completed.exists():
                raise ValidationError(_("Etapas anteriores precisam estar concluídas antes desta etapa."))

# Create your models here.
