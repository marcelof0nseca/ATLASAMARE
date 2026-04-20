from django.db import models
from django.utils.translation import gettext_lazy as _


class MayaConversation(models.Model):
    class Kind(models.TextChoices):
        TREATMENT = "treatment", _("Meu tratamento")
        ROUTINE = "routine", _("Minha rotina")
        FEELINGS = "feelings", _("Como estou me sentindo")

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="maya_conversations")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=220)
    starter_prompt = models.CharField(max_length=180)
    sort_order = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["user", "kind"], name="unique_maya_conversation_per_user_kind"),
        ]
        verbose_name = _("conversa da Maya")
        verbose_name_plural = _("conversas da Maya")

    def __str__(self) -> str:
        return f"{self.user.full_name} - {self.title}"


class AIInteraction(models.Model):
    class Mode(models.TextChoices):
        LLM = "llm", _("LLM")
        FALLBACK = "fallback", _("Fallback")

    class Intent(models.TextChoices):
        TREATMENT = "treatment", _("Tratamento")
        ROUTINE = "routine", _("Rotina")
        FEELINGS = "feelings", _("Acolhimento")
        SYMPTOM = "symptom", _("Sintoma")
        GENERAL = "general", _("Geral")

    class RiskLevel(models.TextChoices):
        LOW = "low", _("Baixo")
        MEDIUM = "medium", _("Medio")
        HIGH = "high", _("Alto")

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="ai_interactions")
    conversation = models.ForeignKey(
        MayaConversation,
        on_delete=models.CASCADE,
        related_name="interactions",
        null=True,
        blank=True,
    )
    question = models.TextField()
    answer = models.TextField()
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.FALLBACK)
    intent = models.CharField(max_length=20, choices=Intent.choices, default=Intent.GENERAL)
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW)
    suggested_next_step = models.CharField(max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("interacao com a Maya")
        verbose_name_plural = _("interacoes com a Maya")

    def __str__(self) -> str:
        return f"{self.user.full_name} - {self.created_at:%d/%m %H:%M}"
