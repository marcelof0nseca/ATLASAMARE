from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from appointments.models import Appointment
from assistant.models import AIInteraction, MayaConversation
from assistant.services import ensure_default_conversations
from core.models import CommunityPost, Partner, PatientTask, TreatmentReport
from medications.models import Medication
from treatments.models import Treatment, TreatmentStep
from users.models import User


class Command(BaseCommand):
    help = "Cria dados demo plausíveis para a Clínica AMARE."

    def handle(self, *args, **options):
        doctor, _ = User.objects.get_or_create(
            email="dra.helen@amare.local",
            defaults={"full_name": "Helen Duarte", "role": User.Role.DOCTOR},
        )
        doctor.set_password("amare123!")
        doctor.save()

        patients = [
            ("ana@amare.local", "Ana Beatriz", True),
            ("luiza@amare.local", "Luiza Mendes", True),
            ("carol@amare.local", "Carol Freitas", False),
        ]
        created_patients = []
        for email, name, reminders in patients:
            patient, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": name,
                    "role": User.Role.PATIENT,
                    "primary_doctor": doctor,
                    "wants_in_app_reminders": reminders,
                },
            )
            patient.primary_doctor = doctor
            patient.wants_in_app_reminders = reminders
            patient.set_password("amare123!")
            patient.save()
            created_patients.append(patient)

        now = timezone.localtime()
        self._seed_treatment_for_ana(created_patients[0], now)
        self._seed_treatment_for_luiza(created_patients[1], now)
        self._seed_empty_state_for_carol(created_patients[2])
        self._seed_explore_content(created_patients, now)
        self.stdout.write(self.style.SUCCESS("Dados demo da Clínica AMARE prontos."))

    def _seed_treatment_for_ana(self, patient, now):
        AIInteraction.objects.filter(user=patient).delete()
        conversations = self._conversation_map(patient)
        treatment, _ = Treatment.objects.get_or_create(
            patient=patient,
            is_active=True,
            defaults={"name": "Fertilização in vitro"},
        )
        step_data = [
            ("Preparação hormonal", 1, TreatmentStep.Status.COMPLETED),
            ("Coleta de óvulos", 2, TreatmentStep.Status.IN_PROGRESS),
            ("Acompanhamento embrionário", 3, TreatmentStep.Status.PENDING),
            ("Transferência embrionária", 4, TreatmentStep.Status.PENDING),
        ]
        self._upsert_steps(treatment, step_data)
        self._seed_appointments(
            patient,
            [
                (Appointment.Type.CONSULTATION, now + timedelta(days=1, hours=2), "Revisão com a médica"),
                (Appointment.Type.EXAM, now + timedelta(days=3, hours=1), "Ultrassom de acompanhamento"),
            ],
        )
        self._seed_medications(
            patient,
            [
                ("Progesterona", now.replace(hour=8, minute=0, second=0, microsecond=0)),
                ("Ácido fólico", now.replace(hour=20, minute=0, second=0, microsecond=0)),
                ("Progesterona", (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)),
            ],
        )
        PatientTask.objects.update_or_create(
            patient=patient,
            title="Separar documentos para a consulta",
            defaults={"notes": "Levar exames recentes se estiverem disponiveis.", "due_at": now + timedelta(hours=4)},
        )
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.TREATMENT],
            question="O que acontece depois da coleta de óvulos?",
            answer="Após a coleta, os óvulos seguem para o laboratório e a equipe acompanha a evolução dos embriões.",
            intent=AIInteraction.Intent.TREATMENT,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Confira a timeline para ver a etapa atual e o que costuma vir depois.",
        )
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.ROUTINE],
            question="Como posso me organizar melhor com as medicações?",
            answer=(
                "Comece olhando apenas a próxima dose pendente e depois as demais medicações do dia. "
                "Se surgir dúvida sobre mudar dose, horário ou uso, fale com sua equipe médica."
            ),
            intent=AIInteraction.Intent.ROUTINE,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Abra a rotina e confirme a próxima dose antes de olhar o resto do dia.",
        )
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.FEELINGS],
            question="Estou com medo de não dar conta dessa fase.",
            answer=(
                "Sinto muito que este momento esteja pesado. Você não precisa resolver tudo de uma vez. "
                "Se quiser, podemos olhar juntas apenas o próximo passo concreto do dia."
            ),
            intent=AIInteraction.Intent.FEELINGS,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Escolha um passo pequeno para agora, como revisar a próxima consulta ou dose.",
        )

    def _seed_treatment_for_luiza(self, patient, now):
        AIInteraction.objects.filter(user=patient).delete()
        conversations = self._conversation_map(patient)
        treatment, _ = Treatment.objects.get_or_create(
            patient=patient,
            is_active=True,
            defaults={"name": "Congelamento de óvulos"},
        )
        step_data = [
            ("Consulta inicial", 1, TreatmentStep.Status.COMPLETED),
            ("Exames preparatórios", 2, TreatmentStep.Status.COMPLETED),
            ("Estimulação ovariana", 3, TreatmentStep.Status.COMPLETED),
            ("Coleta programada", 4, TreatmentStep.Status.PENDING),
        ]
        self._upsert_steps(treatment, step_data)
        self._seed_appointments(
            patient,
            [(Appointment.Type.EXAM, now + timedelta(days=5, hours=3), "Exames finais antes da coleta")],
        )
        self._seed_medications(
            patient,
            [("Vitamina D", now.replace(hour=9, minute=30, second=0, microsecond=0))],
        )
        report, _ = TreatmentReport.objects.get_or_create(
            patient=patient,
            title="Laudo pos-tratamento",
            defaults={"status": TreatmentReport.Status.AVAILABLE, "release_note": "Liberado pela equipe AMARE."},
        )
        if not report.file:
            report.file.save("laudo-demo.txt", ContentFile("Laudo demo AMARE para validacao da jornada."), save=True)
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.TREATMENT],
            question="Qual costuma ser o próximo passo do tratamento?",
            answer=(
                "De forma geral, o próximo passo costuma ser a coleta programada. "
                "A timeline ajuda a acompanhar isso sem precisar guardar tudo de cabeça."
            ),
            intent=AIInteraction.Intent.TREATMENT,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Veja a timeline para conferir a etapa atual e a próxima.",
        )
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.ROUTINE],
            question="Como a agenda me ajuda a acompanhar consultas e exames?",
            answer=(
                "A agenda mostra os compromissos em ordem de data para você olhar primeiro o que vem mais cedo "
                "e seguir por partes."
            ),
            intent=AIInteraction.Intent.ROUTINE,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Abra a agenda e veja apenas o próximo compromisso.",
        )

    def _seed_empty_state_for_carol(self, patient):
        AIInteraction.objects.filter(user=patient).delete()
        conversations = self._conversation_map(patient)
        Treatment.objects.filter(patient=patient).delete()
        Appointment.objects.filter(patient=patient).delete()
        Medication.objects.filter(patient=patient).delete()
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.TREATMENT],
            question="Como acompanho meu próximo passo?",
            answer=(
                "Quando a clínica iniciar ou atualizar seu tratamento, a etapa atual e o próximo passo "
                "aparecem logo no início da plataforma."
            ),
            intent=AIInteraction.Intent.TREATMENT,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Quando houver uma nova atualização, a timeline vai mostrar o caminho com clareza.",
        )
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.FEELINGS],
            question="Estou ansiosa porque ainda não comecei.",
            answer=(
                "É compreensível se sentir assim. Quando o tratamento ainda não começou, a espera também pode pesar. "
                "Podemos seguir por partes e olhar apenas o próximo movimento esperado."
            ),
            intent=AIInteraction.Intent.FEELINGS,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Se ajudar, acompanhe apenas quando a clínica atualizar a próxima etapa.",
        )

    def _seed_explore_content(self, patients, now):
        partner_data = [
            (
                "Clara Nunes",
                Partner.Category.PSYCHOLOGY,
                "Psicologia perinatal",
                "Apoio emocional para momentos de ansiedade, espera e tomada de decisao.",
                "ansiedade,acolhimento,online",
                True,
            ),
            (
                "Viva Nutrir",
                Partner.Category.NUTRITION,
                "Nutricao para fertilidade",
                "Orientacao nutricional complementar para rotina alimentar durante o tratamento.",
                "fertilidade,rotina,planejamento",
                True,
            ),
            (
                "Ponto de Equilibrio",
                Partner.Category.ACUPUNCTURE,
                "Acupuntura integrativa",
                "Servico complementar voltado a relaxamento e bem-estar.",
                "bem-estar,relaxamento,presencial",
                False,
            ),
        ]
        for index, (name, category, specialty, description, tags, featured) in enumerate(partner_data, start=1):
            Partner.objects.update_or_create(
                name=name,
                defaults={
                    "category": category,
                    "specialty": specialty,
                    "description": description,
                    "tags": tags,
                    "contact_url": "https://wa.me/5581998003535",
                    "is_featured": featured,
                    "is_active": True,
                    "sort_order": index,
                },
            )

        approved_posts = [
            (
                patients[0],
                CommunityPost.Category.FEELINGS,
                "No dia em que eu parei de tentar entender tudo de uma vez, a rotina ficou um pouco mais possivel.",
            ),
            (
                patients[1],
                CommunityPost.Category.ROUTINE,
                "O que mais me ajudou foi olhar primeiro a proxima dose e depois a agenda. Uma coisa por vez.",
            ),
        ]
        for author, category, body in approved_posts:
            CommunityPost.objects.update_or_create(
                author=author,
                body=body,
                defaults={
                    "category": category,
                    "pseudonym": "Paciente AMARE",
                    "status": CommunityPost.Status.APPROVED,
                    "approved_at": now,
                },
            )

    def _conversation_map(self, patient):
        return {
            conversation.kind: conversation
            for conversation in ensure_default_conversations(patient)
        }

    def _upsert_steps(self, treatment, steps):
        for name, order, status in steps:
            TreatmentStep.objects.update_or_create(
                treatment=treatment,
                order=order,
                defaults={"name": name, "status": status},
            )

    def _seed_appointments(self, patient, items):
        for appointment_type, scheduled_at, details in items:
            Appointment.objects.get_or_create(
                patient=patient,
                type=appointment_type,
                scheduled_at=scheduled_at,
                defaults={"details": details},
            )

    def _seed_medications(self, patient, items):
        for name, scheduled_for in items:
            Medication.objects.get_or_create(
                patient=patient,
                name=name,
                scheduled_for=scheduled_for,
            )

    def _upsert_interaction(self, user, conversation, question, answer, intent, risk_level, suggested_next_step):
        AIInteraction.objects.update_or_create(
            user=user,
            conversation=conversation,
            question=question,
            defaults={
                "answer": answer,
                "mode": AIInteraction.Mode.FALLBACK,
                "intent": intent,
                "risk_level": risk_level,
                "suggested_next_step": suggested_next_step,
            },
        )
