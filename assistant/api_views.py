from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsPatientUser

from .serializers import AIInteractionSerializer, MayaConversationSerializer
from .services import (
    answer_question_with_maya,
    ensure_default_conversations,
    get_conversation_or_default,
)


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
    conversation_kind = serializers.ChoiceField(
        choices=["treatment", "routine", "feelings"],
        required=False,
    )


class MayaConversationListAPIView(APIView):
    permission_classes = [IsPatientUser]

    def get(self, request):
        conversations = ensure_default_conversations(request.user)
        return Response(MayaConversationSerializer(conversations, many=True).data)


class AIInteractionListCreateAPIView(APIView):
    permission_classes = [IsPatientUser]

    def get(self, request):
        conversation = get_conversation_or_default(
            request.user,
            request.query_params.get("conversation_kind"),
        )
        interactions = list(conversation.interactions.order_by("-created_at")[:20])[::-1]
        return Response(
            {
                "conversation": MayaConversationSerializer(conversation).data,
                "interactions": AIInteractionSerializer(interactions, many=True).data,
            }
        )

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = get_conversation_or_default(
            request.user,
            serializer.validated_data.get("conversation_kind"),
        )
        try:
            interaction = answer_question_with_maya(
                request.user,
                serializer.validated_data["question"],
                conversation=conversation,
            )
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AIInteractionSerializer(interaction).data)
