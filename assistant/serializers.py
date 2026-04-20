from rest_framework import serializers

from .models import AIInteraction, MayaConversation


class MayaConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MayaConversation
        fields = ["id", "kind", "title", "description", "starter_prompt", "sort_order"]


class AIInteractionSerializer(serializers.ModelSerializer):
    conversation_kind = serializers.CharField(source="conversation.kind", read_only=True)
    conversation_title = serializers.CharField(source="conversation.title", read_only=True)

    class Meta:
        model = AIInteraction
        fields = [
            "id",
            "conversation_kind",
            "conversation_title",
            "question",
            "answer",
            "mode",
            "intent",
            "risk_level",
            "suggested_next_step",
            "created_at",
        ]
