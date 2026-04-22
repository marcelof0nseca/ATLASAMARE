from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from appointments.models import Appointment
from assistant.models import AIInteraction, MayaConversation
from assistant.services import ensure_default_conversations
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
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.TREATMENT],
            question="O que acontece depois da coleta de óvulos?",
            answer=(
                "Depois da coleta, os óvulos seguem para o laboratório e os embriões passam a ser acompanhados pela equipe médica. "
                "Se quiser, eu também posso te explicar o que costuma vir depois dessa etapa."
            ),
            intent=AIInteraction.Intent.TREATMENT,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Confira a timeline para ver a etapa atual e o que costuma vir depois. Se quiser, eu posso te explicar cada parte.",
        )
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.ROUTINE],
            question="Como posso me organizar melhor com as medicações?",
            answer=(
                "Para ficar mais leve, vamos olhar só a próxima dose primeiro e deixar o resto para depois. "
                "Se surgir dúvida sobre mudar dose, horário ou uso, fale com sua equipe médica."
            ),
            intent=AIInteraction.Intent.ROUTINE,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Abra a rotina e confirme a próxima dose antes de olhar o resto do dia. Se quiser, eu posso seguir com você depois disso.",
        )
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.FEELINGS],
            question="Estou com medo de não dar conta dessa fase.",
            answer=(
                "Ana, sinto muito que este momento esteja pesado. Você não precisa dar conta de tudo agora. "
                "Vamos por partes e olhar só o próximo passo concreto do dia."
            ),
            intent=AIInteraction.Intent.FEELINGS,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Escolha um passo pequeno para agora, como revisar a próxima consulta ou dose. Se quiser, continue me contando o que está pesando mais.",
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
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.TREATMENT],
            question="Qual costuma ser o próximo passo do tratamento?",
            answer=(
                "Vamos olhar só o próximo passo. De forma geral, ele costuma ser a coleta programada. "
                "A timeline ajuda a acompanhar isso sem precisar guardar tudo de cabeça."
            ),
            intent=AIInteraction.Intent.TREATMENT,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Veja a timeline para conferir a etapa atual e a próxima. Se quiser, eu posso te explicar cada parte.",
        )
        self._upsert_interaction(
            user=patient,
            conversation=conversations[MayaConversation.Kind.ROUTINE],
            question="Como a agenda me ajuda a acompanhar consultas e exames?",
            answer=(
                "Você não precisa organizar o dia inteiro de uma vez. A agenda mostra os compromissos em ordem de data "
                "para você olhar primeiro o que vem mais cedo e seguir por partes."
            ),
            intent=AIInteraction.Intent.ROUTINE,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Abra a agenda e veja apenas o próximo compromisso. Se quiser, depois voltamos para o restante.",
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
                "Quando a clínica iniciar ou atualizar seu tratamento, a etapa atual e o próximo passo aparecem logo no início da plataforma. "
                "Se quiser, eu posso te ajudar a entender isso assim que surgir uma atualização."
            ),
            intent=AIInteraction.Intent.TREATMENT,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Quando houver uma nova atualização, a timeline vai mostrar o caminho com clareza. Se quiser, eu posso olhar isso com você.",
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
            suggested_next_step="Se ajudar, acompanhe apenas quando a clínica atualizar a próxima etapa. Se quiser, continue me contando como você está se sentindo.",
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
