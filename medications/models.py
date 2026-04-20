from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Medication(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pendente")
        COMPLETED = "completed", _("Concluído")

    patient = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="medications",
        limit_choices_to={"role": "patient"},
    )
    name = models.CharField(max_length=120)
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_for"]
        verbose_name = _("dose de medicação")
        verbose_name_plural = _("doses de medicação")

    def __str__(self) -> str:
        return f"{self.name} - {self.patient.full_name}"

    def clean(self) -> None:
        super().clean()
        if not self.patient.is_patient:
            raise ValidationError({"patient": _("Medicações devem estar associadas a uma paciente.")})
        if self.status == self.Status.COMPLETED and not self.completed_at:
            raise ValidationError({"completed_at": _("Informe quando a medicação foi concluída.")})

# Create your models here.
