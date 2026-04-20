from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Appointment(models.Model):
    class Type(models.TextChoices):
        CONSULTATION = "consultation", _("Consulta")
        EXAM = "exam", _("Exame")

    patient = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="appointments",
        limit_choices_to={"role": "patient"},
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    scheduled_at = models.DateTimeField()
    details = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_at"]
        verbose_name = _("compromisso")
        verbose_name_plural = _("compromissos")

    def __str__(self) -> str:
        return f"{self.get_type_display()} - {self.patient.full_name}"

    def clean(self) -> None:
        super().clean()
        if not self.patient.is_patient:
            raise ValidationError({"patient": _("Compromissos devem estar associados a uma paciente.")})

# Create your models here.
