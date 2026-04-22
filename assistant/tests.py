from datetime import timedelta

from django.test import Client, TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from appointments.models import Appointment
from medications.models import Medication
from treatments.models import Treatment, TreatmentStep
from users.models import User

from .models import AIInteraction, MayaConversation
from .services import answer_question_with_maya, ensure_default_conversations
from .views import MayaSendMessageView


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
            scheduled_for=timezone.now() + timedelta(hours=2),
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
        interaction = answer_question_with_maya(
            self.patient,
            "Estou com dor forte, devo mudar o remédio?",
            conversation=self.conversations[MayaConversation.Kind.FEELINGS],
        )
        self.assertEqual(interaction.mode, AIInteraction.Mode.FALLBACK)
        self.assertEqual(interaction.intent, AIInteraction.Intent.SYMPTOM)
        self.assertEqual(interaction.risk_level, AIInteraction.RiskLevel.HIGH)
        self.assertIn("equipe médica", interaction.answer.lower())

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
