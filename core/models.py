from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PatientTask(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pendente")
        COMPLETED = "completed", _("Concluida")

    patient = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="personal_tasks",
        limit_choices_to={"role": "patient"},
    )
    title = models.CharField(max_length=120)
    notes = models.CharField(max_length=220, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "due_at", "-created_at"]
        verbose_name = _("tarefa pessoal")
        verbose_name_plural = _("tarefas pessoais")

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        if self.patient_id and not self.patient.is_patient:
            raise ValidationError({"patient": _("Tarefas pessoais devem estar associadas a uma paciente.")})

    def complete(self):
        if self.status == self.Status.COMPLETED:
            return self
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])
        return self


class TreatmentReport(models.Model):
    class Status(models.TextChoices):
        LOCKED = "locked", _("Bloqueado")
        AVAILABLE = "available", _("Liberado")

    patient = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="treatment_reports",
        limit_choices_to={"role": "patient"},
    )
    title = models.CharField(max_length=120, default="Laudo pos-tratamento")
    file = models.FileField(upload_to="reports/", blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LOCKED)
    release_note = models.CharField(max_length=220, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("laudo de tratamento")
        verbose_name_plural = _("laudos de tratamento")

    def __str__(self) -> str:
        return f"{self.title} - {self.patient.full_name}"

    @property
    def is_available(self) -> bool:
        return self.status == self.Status.AVAILABLE and bool(self.file)


class Partner(models.Model):
    class Category(models.TextChoices):
        PSYCHOLOGY = "psychology", _("Psicologia")
        NUTRITION = "nutrition", _("Nutricao")
        ACUPUNCTURE = "acupuncture", _("Acupuntura")
        PHYSIOTHERAPY = "physiotherapy", _("Fisioterapia")
        WELLBEING = "wellbeing", _("Bem-estar")

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=30, choices=Category.choices)
    specialty = models.CharField(max_length=140)
    description = models.CharField(max_length=260)
    tags = models.CharField(max_length=180, blank=True, help_text=_("Separe por virgulas."))
    contact_label = models.CharField(max_length=80, default="Entrar em contato")
    contact_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = _("parceiro multidisciplinar")
        verbose_name_plural = _("parceiros multidisciplinares")

    def __str__(self) -> str:
        return self.name

    @property
    def tag_list(self) -> list[str]:
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


class SupportCommunity(models.Model):
    class Category(models.TextChoices):
        EMOTIONAL = "emotional", _("Apoio emocional")
        FERTILITY = "fertility", _("Fertilidade")
        ROUTINE = "routine", _("Rotina")
        FAMILY = "family", _("Familia e rede")
        WELLBEING = "wellbeing", _("Bem-estar")

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=30, choices=Category.choices)
    audience = models.CharField(max_length=140)
    description = models.CharField(max_length=320)
    support_type = models.CharField(max_length=120)
    contact_label = models.CharField(max_length=80, default="Acessar comunidade")
    contact_url = models.URLField()
    tags = models.CharField(max_length=180, blank=True, help_text=_("Separe por virgulas."))
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = _("comunidade de apoio")
        verbose_name_plural = _("comunidades de apoio")

    def __str__(self) -> str:
        return self.name

    @property
    def tag_list(self) -> list[str]:
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


class CommunityPost(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pendente")
        APPROVED = "approved", _("Aprovado")
        REJECTED = "rejected", _("Rejeitado")

    class Category(models.TextChoices):
        TREATMENT = "treatment", _("Tratamento")
        ROUTINE = "routine", _("Rotina")
        FEELINGS = "feelings", _("Acolhimento")
        HOPE = "hope", _("Esperanca")

    author = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="community_posts",
        limit_choices_to={"role": "patient"},
    )
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.FEELINGS)
    body = models.TextField(max_length=900)
    pseudonym = models.CharField(max_length=80, default="Paciente AMARE")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    moderation_note = models.CharField(max_length=220, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-approved_at", "-created_at"]
        verbose_name = _("relato da comunidade")
        verbose_name_plural = _("relatos da comunidade")

    def __str__(self) -> str:
        return f"{self.get_category_display()} - {self.pseudonym}"

    @property
    def support_count(self) -> int:
        # len() usa o cache do prefetch_related("reactions") quando disponível.
        # .count() sempre gera um SELECT COUNT(*) extra, ignorando o cache.
        return len(self.reactions.all())


class CommunityReaction(models.Model):
    class Kind(models.TextChoices):
        SUPPORT = "support", _("Apoio")

    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="reactions")
    patient = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="community_reactions",
        limit_choices_to={"role": "patient"},
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.SUPPORT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "patient"], name="unique_community_reaction_per_patient")
        ]
        verbose_name = _("reacao da comunidade")
        verbose_name_plural = _("reacoes da comunidade")

    def __str__(self) -> str:
        return f"{self.patient.full_name} -> {self.post_id}"
