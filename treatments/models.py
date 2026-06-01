import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
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
        # self.steps.all() usa o cache do prefetch_related quando disponível.
        # self.steps.filter() sempre gera uma nova query SQL, ignorando o cache.
        return next(
            (s for s in self.steps.all() if s.status == TreatmentStep.Status.IN_PROGRESS),
            None,
        )

    @property
    def next_step(self):
        # Itera o cache de steps uma única vez para encontrar current e next.
        steps = list(self.steps.all())  # ordenado por `order` via Meta
        current = next((s for s in steps if s.status == TreatmentStep.Status.IN_PROGRESS), None)
        if current:
            return next((s for s in steps if s.order > current.order), None)
        return next((s for s in steps if s.status != TreatmentStep.Status.COMPLETED), None)


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


class JourneyDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=160)
    week = models.PositiveSmallIntegerField()
    uploaded_at = models.DateTimeField()
    size_label = models.CharField(max_length=24)
    file = models.FileField(upload_to="journey_documents/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["week", "uploaded_at", "name"]
        verbose_name = _("documento da jornada")
        verbose_name_plural = _("documentos da jornada")

    def __str__(self) -> str:
        return f"Semana {self.week} - {self.name}"

    @property
    def original_name(self) -> str:
        return self.name

    @property
    def file_url(self) -> str:
        return self.file.url if self.file else ""

    def get_download_url(self) -> str:
        return reverse("treatments:documents-download", args=[self.id])


class JourneyVideo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=160)
    description = models.TextField()
    step = models.PositiveSmallIntegerField()
    video_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to="journey_videos/", blank=True)
    thumbnail_url = models.URLField(blank=True)
    thumbnail_file = models.FileField(upload_to="journey_video_thumbnails/", blank=True)
    duration = models.CharField(max_length=24, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["step", "title"]
        verbose_name = _("vídeo da jornada")
        verbose_name_plural = _("vídeos da jornada")

    def __str__(self) -> str:
        return f"Etapa {self.step} - {self.title}"

    @property
    def video_source(self) -> str:
        if self.video_file:
            return self.video_file.url
        return self.video_url

    @property
    def thumbnail_source(self) -> str:
        if self.thumbnail_file:
            return self.thumbnail_file.url
        return self.thumbnail_url


# Create your models here.
