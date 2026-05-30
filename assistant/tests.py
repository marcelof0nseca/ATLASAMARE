from datetime import timedelta
import json
from urllib import error
from unittest.mock import patch

from django.test import Client, TestCase, override_settings
from django.urls import resolve, reverse
from django.utils import timezone

from appointments.models import Appointment
from medications.models import Medication
from treatments.models import Treatment, TreatmentStep
from users.models import User

from .models import AIInteraction, MayaConversation
from .services import answer_question_with_maya, ensure_default_conversations
from .views import MayaSendMessageView


class FakeLLMResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class MayaConversationTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(
            email="patient@amare.local",
            password="amare123!",
            full_name="Paciente",
            role=User.Role.PATIENT,
        )
        self.treatment = Treatment.objects.create(
            patient=self.patient,
            name="FIV",
            is_active=True,
        )
        TreatmentStep.objects.create(
            treatment=self.treatment,
            name="Preparação hormonal",
            order=1,
            status=TreatmentStep.Status.COMPLETED,
        )
        TreatmentStep.objects.create(
            treatment=self.treatment,
            name="Coleta de óvulos",
            order=2,
            status=TreatmentStep.Status.IN_PROGRESS,
        )
        TreatmentStep.objects.create(
            treatment=self.treatment,
            name="Acompanhamento embrionário",
            order=3,
            status=TreatmentStep.Status.PENDING,
        )
        Medication.objects.create(
            patient=self.patient,
            name="Progesterona",
            scheduled_for=timezone.localtime().replace(hour=20, minute=0, second=0, microsecond=0),
        )
        Appointment.objects.create(
            patient=self.patient,
            type=Appointment.Type.CONSULTATION,
            scheduled_at=timezone.now() + timedelta(days=1),
            details="Retorno com a equipe",
        )
        self.conversations = {
            conversation.kind: conversation
            for conversation in ensure_default_conversations(self.patient)
        }

    def test_default_conversations_are_created_for_patient(self):
        self.assertEqual(len(self.conversations), 3)
        self.assertEqual(
            set(self.conversations.keys()),
            {
                MayaConversation.Kind.TREATMENT,
                MayaConversation.Kind.ROUTINE,
                MayaConversation.Kind.FEELINGS,
            },
        )

    def test_routine_question_uses_routine_conversation_and_specific_fallback(self):
        interaction = answer_question_with_maya(
            self.patient,
            "Como posso me organizar melhor com as medicações?",
            conversation=self.conversations[MayaConversation.Kind.ROUTINE],
        )
        self.assertEqual(interaction.mode, AIInteraction.Mode.FALLBACK)
        self.assertEqual(interaction.conversation.kind, MayaConversation.Kind.ROUTINE)
        self.assertEqual(interaction.intent, AIInteraction.Intent.ROUTINE)
        self.assertIn("próxima dose", interaction.answer.lower())
        self.assertIn("próximo compromisso", interaction.suggested_next_step.lower())

    def test_next_step_question_mentions_next_step(self):
        interaction = answer_question_with_maya(
            self.patient,
            "Qual é o próximo passo do tratamento?",
            conversation=self.conversations[MayaConversation.Kind.TREATMENT],
        )
        self.assertEqual(interaction.mode, AIInteraction.Mode.FALLBACK)
        self.assertEqual(interaction.intent, AIInteraction.Intent.TREATMENT)
        self.assertIn("acompanhamento embrionário", interaction.answer.lower())

    def test_feelings_conversation_returns_supportive_answer(self):
        interaction = answer_question_with_maya(
            self.patient,
            "Estou me sentindo muito ansiosa hoje.",
            conversation=self.conversations[MayaConversation.Kind.FEELINGS],
        )
        self.assertEqual(interaction.mode, AIInteraction.Mode.FALLBACK)
        self.assertEqual(interaction.intent, AIInteraction.Intent.FEELINGS)
        self.assertIn("você não precisa resolver tudo de uma vez", interaction.answer.lower())
        self.assertIn("próximo passo", interaction.suggested_next_step.lower())

    def test_sensitive_symptom_in_feelings_conversation_redirects_to_team(self):
        with patch("assistant.services.urllib_request.urlopen") as urlopen_mock:
            interaction = answer_question_with_maya(
                self.patient,
                "Estou com dor forte, devo mudar o remédio?",
                conversation=self.conversations[MayaConversation.Kind.FEELINGS],
            )
        self.assertEqual(interaction.mode, AIInteraction.Mode.FALLBACK)
        self.assertEqual(interaction.intent, AIInteraction.Intent.SYMPTOM)
        self.assertEqual(interaction.risk_level, AIInteraction.RiskLevel.HIGH)
        self.assertIn("equipe médica", interaction.answer.lower())
        urlopen_mock.assert_not_called()

    @override_settings(MAYA_LLM_PROVIDER="gemini", MAYA_GEMINI_API_KEY="", MAYA_GEMINI_MODEL="gemini-3.5-flash")
    def test_gemini_without_key_uses_fallback(self):
        with patch("assistant.services.urllib_request.urlopen") as urlopen_mock:
            interaction = answer_question_with_maya(
                self.patient,
                "Qual e o proximo passo do tratamento?",
                conversation=self.conversations[MayaConversation.Kind.TREATMENT],
            )

        self.assertEqual(interaction.mode, AIInteraction.Mode.FALLBACK)
        urlopen_mock.assert_not_called()

    @override_settings(
        MAYA_LLM_PROVIDER="gemini",
        MAYA_GEMINI_API_KEY="test-key",
        MAYA_GEMINI_MODEL="gemini-3.5-flash",
        MAYA_GEMINI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    )
    def test_gemini_provider_builds_chat_completions_payload(self):
        with patch("assistant.services.urllib_request.urlopen") as urlopen_mock:
            urlopen_mock.return_value = FakeLLMResponse(
                {"choices": [{"message": {"content": "Resposta gerada pela Gemini."}}]}
            )
            interaction = answer_question_with_maya(
                self.patient,
                "Me explica minha etapa atual?",
                conversation=self.conversations[MayaConversation.Kind.TREATMENT],
            )

        request = urlopen_mock.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(interaction.mode, AIInteraction.Mode.LLM)
        self.assertEqual(interaction.answer, "Resposta gerada pela Gemini.")
        self.assertEqual(payload["model"], "gemini-3.5-flash")
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["messages"][1]["role"], "user")
        self.assertIn("Bearer test-key", request.headers["Authorization"])

    @override_settings(
        MAYA_LLM_PROVIDER="gemini",
        MAYA_GEMINI_API_KEY="test-key",
        MAYA_GEMINI_MODEL="gemini-3.5-flash",
    )
    def test_gemini_api_error_falls_back(self):
        with patch("assistant.services.urllib_request.urlopen") as urlopen_mock:
            urlopen_mock.side_effect = error.URLError("timeout")
            interaction = answer_question_with_maya(
                self.patient,
                "Como posso me organizar com a agenda?",
                conversation=self.conversations[MayaConversation.Kind.ROUTINE],
            )

        self.assertEqual(interaction.mode, AIInteraction.Mode.FALLBACK)
        self.assertEqual(interaction.intent, AIInteraction.Intent.ROUTINE)

    @override_settings(
        MAYA_LLM_PROVIDER="groq",
        MAYA_GROQ_API_KEY="groq-key",
        MAYA_GROQ_MODEL="llama-3.1-8b-instant",
        MAYA_GROQ_BASE_URL="https://api.groq.com/openai/v1/chat/completions",
    )
    def test_groq_provider_builds_chat_completions_payload(self):
        with patch("assistant.services.urllib_request.urlopen") as urlopen_mock:
            urlopen_mock.return_value = FakeLLMResponse(
                {"choices": [{"message": {"content": "Resposta gerada pela Groq."}}]}
            )
            interaction = answer_question_with_maya(
                self.patient,
                "Me explica minha etapa atual?",
                conversation=self.conversations[MayaConversation.Kind.TREATMENT],
            )

        request = urlopen_mock.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(interaction.mode, AIInteraction.Mode.LLM)
        self.assertEqual(interaction.answer, "Resposta gerada pela Groq.")
        self.assertEqual(payload["model"], "llama-3.1-8b-instant")
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["messages"][1]["role"], "user")
        self.assertIn("Bearer groq-key", request.headers["Authorization"])
        self.assertEqual(request.headers["Accept"], "application/json")
        self.assertEqual(request.headers["User-agent"], "Clinica-AMARE/1.0")

    @override_settings(
        MAYA_LLM_PROVIDER="groq",
        MAYA_GROQ_API_KEY="groq-key",
        MAYA_GROQ_MODEL="llama-3.1-8b-instant",
        MAYA_GROQ_BASE_URL="https://api.groq.com/openai/v1/chat/completions",
    )
    def test_general_greeting_uses_llm_when_groq_is_configured(self):
        with patch("assistant.services.urllib_request.urlopen") as urlopen_mock:
            urlopen_mock.return_value = FakeLLMResponse(
                {"choices": [{"message": {"content": "Oi! Estou bem e pronta para te acompanhar."}}]}
            )
            interaction = answer_question_with_maya(
                self.patient,
                "Oi, tudo bem?",
                conversation=self.conversations[MayaConversation.Kind.TREATMENT],
            )

        self.assertEqual(interaction.mode, AIInteraction.Mode.LLM)
        self.assertEqual(interaction.intent, AIInteraction.Intent.GENERAL)
        self.assertIn("pronta", interaction.answer.lower())

    def test_send_route_resolves_to_send_view(self):
        match = resolve("/maya/send/")
        self.assertEqual(match.func.view_class, MayaSendMessageView)

    def test_patient_can_post_message_to_send_route(self):
        client = Client()
        client.force_login(self.patient)
        response = client.post(
            reverse("assistant:send"),
            {
                "conversation_kind": MayaConversation.Kind.ROUTINE,
                "question": "Como posso me organizar melhor com as medicações?",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            AIInteraction.objects.filter(
                user=self.patient,
                conversation__kind=MayaConversation.Kind.ROUTINE,
                question="Como posso me organizar melhor com as medicações?",
            ).exists()
        )
