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
    push_notifications_enabled = models.BooleanField(default=False, verbose_name=_("notificações web ativas"))

    # ── Dados pessoais ────────────────────────────────────────────────────────
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name=_("telefone"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("data de nascimento"))
    emergency_contact_name = models.CharField(max_length=150, blank=True, default="", verbose_name=_("nome do contato de emergência"))
    emergency_contact_phone = models.CharField(max_length=20, blank=True, default="", verbose_name=_("telefone do contato de emergência"))

    # ── Notificações por e-mail ───────────────────────────────────────────────
    class ReminderFrequency(models.TextChoices):
        ON_UPDATE = "on_update", _("Apenas quando houver novidade")
        DAILY     = "daily",     _("Diariamente")
        WEEKLY    = "weekly",    _("Semanalmente")

    email_reminders_appointments = models.BooleanField(default=True, verbose_name=_("lembretes de consulta por e-mail"))
    email_reminders_journey      = models.BooleanField(default=True, verbose_name=_("atualizações da jornada por e-mail"))
    email_reminders_maya         = models.BooleanField(default=False, verbose_name=_("resumos da Maya por e-mail"))
    reminder_frequency = models.CharField(
        max_length=20,
        choices=ReminderFrequency.choices,
        default=ReminderFrequency.ON_UPDATE,
        verbose_name=_("frequência dos lembretes"),
    )

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
    def preferred_name(self) -> str:
        return self.full_name.split()[0] if self.full_name else ""

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
