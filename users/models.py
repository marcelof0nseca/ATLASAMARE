from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = "patient", _("Paciente")
        DOCTOR = "doctor", _("Médico")
        PARTNER = "partner", _("Acompanhante")

    username = None
    first_name = None
    last_name = None

    full_name = models.CharField(max_length=150, verbose_name=_("nome"))
    email = models.EmailField(unique=True, verbose_name=_("email"))
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
        verbose_name=_("papel"),
    )
    primary_doctor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="patients",
        null=True,
        blank=True,
        limit_choices_to={"role": Role.DOCTOR},
        verbose_name=_("médico responsável"),
    )
    linked_patient = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="partners",
        null=True,
        blank=True,
        limit_choices_to={"role": Role.PATIENT},
        verbose_name=_("paciente acompanhado"),
    )
    wants_in_app_reminders = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        ordering = ["full_name"]
        verbose_name = _("usuário")
        verbose_name_plural = _("usuários")

    def __str__(self) -> str:
        return self.full_name

    @property
    def is_patient(self) -> bool:
        return self.role == self.Role.PATIENT

    @property
    def is_doctor(self) -> bool:
        return self.role == self.Role.DOCTOR

    @property
    def is_partner(self) -> bool:
        return self.role == self.Role.PARTNER

    def clean(self) -> None:
        super().clean()
        if self.is_doctor and self.primary_doctor_id:
            raise ValidationError({"primary_doctor": _("Médicos não devem ter médico responsável.")})
        if self.primary_doctor and not self.is_patient:
            raise ValidationError({"role": _("Apenas pacientes podem ter médico responsável.")})
        if self.linked_patient and not self.is_partner:
            raise ValidationError({"role": _("Apenas acompanhantes podem ter um paciente acompanhado.")})

# Create your models here.
