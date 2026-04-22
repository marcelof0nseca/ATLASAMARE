import json
import unicodedata
from dataclasses import dataclass
from urllib import error, request as urllib_request

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from appointments.models import Appointment
from medications.models import Medication
from treatments.models import Treatment

from .models import AIInteraction, MayaConversation


CONVERSATION_BLUEPRINTS = {
    MayaConversation.Kind.TREATMENT: {
        "title": "Meu tratamento",
        "description": "Entenda as etapas com calma, previsibilidade e linguagem simples.",
        "starter_prompt": "Pergunte sobre etapas, exames ou o que costuma vir depois.",
        "sort_order": 1,
        "examples": [
            "O que acontece depois da coleta de óvulos?",
            "Qual costuma ser o próximo passo do tratamento?",
            "Como funciona a transferência embrionária?",
        ],
        "empty_title": "Esta conversa ajuda você a entender o caminho do tratamento.",
        "empty_copy": "Se quiser, podemos olhar uma etapa de cada vez para tudo ficar mais claro.",
    },
    MayaConversation.Kind.ROUTINE: {
        "title": "Minha rotina",
        "description": "Organize medicações, agenda e o que merece atenção hoje sem sobrecarga.",
        "starter_prompt": "Pergunte sobre medicações, horários, agenda e organização do dia.",
        "sort_order": 2,
        "examples": [
            "Como posso me organizar melhor com as medicações?",
            "O que preciso olhar primeiro hoje?",
            "Como a agenda me ajuda a acompanhar consultas e exames?",
        ],
        "empty_title": "Esta conversa foi feita para deixar o dia mais leve.",
        "empty_copy": "Se quiser, começamos só pela próxima dose ou pelo próximo compromisso.",
    },
    MayaConversation.Kind.FEELINGS: {
        "title": "Como estou me sentindo",
        "description": "Receba acolhimento emocional e orientação segura quando este momento pesar.",
        "starter_prompt": "Fale sobre medo, ansiedade, insegurança ou sintomas para receber apoio seguro.",
        "sort_order": 3,
        "examples": [
            "Estou me sentindo ansiosa hoje.",
            "Estou com medo de não dar conta dessa fase.",
            "Estou com dor e isso está me assustando.",
        ],
        "empty_title": "Esta conversa acolhe você com calma, sem substituir a equipe médica.",
        "empty_copy": "Você pode falar sobre medo, ansiedade, insegurança ou sintomas. Se algo pedir cuidado médico, a Maya vai ser transparente.",
    },
}

TREATMENT_KEYWORDS = [
    "tratamento",
    "etapa",
    "etapas",
    "coleta",
    "ovulo",
    "ovulos",
    "embriao",
    "embrioes",
    "fertilizacao",
    "transferencia",
    "timeline",
    "proximo passo",
    "proxima etapa",
]

ROUTINE_KEYWORDS = [
    "agenda",
    "consulta",
    "consultas",
    "exame",
    "exames",
    "compromisso",
    "compromissos",
    "medicacao",
    "medicacoes",
    "medicamento",
    "medicamentos",
    "remedio",
    "remedios",
    "horario",
    "horarios",
    "rotina",
    "organizar",
]

FEELINGS_KEYWORDS = [
    "ansiosa",
    "ansioso",
    "ansiedade",
    "medo",
    "triste",
    "tristeza",
    "frustrada",
    "frustrado",
    "nervosa",
    "nervoso",
    "insegura",
    "inseguro",
    "sobrecarregada",
    "sobrecarregado",
    "angustiada",
    "angustiado",
    "angustia",
    "preocupada",
    "preocupado",
    "preocupacao",
    "sozinha",
    "sozinho",
    "cansada",
    "cansado",
    "chorando",
    "abalada",
    "abalado",
]

SYMPTOM_KEYWORDS = [
    "dor",
    "colica",
    "enjoo",
    "nausea",
    "tontura",
    "inchaco",
    "inchada",
    "inchado",
    "mal estar",
    "desconforto",
    "sintoma",
    "sintomas",
]

HIGH_RISK_KEYWORDS = [
    "dor forte",
    "muita dor",
    "dor intensa",
    "sangramento",
    "falta de ar",
    "febre",
    "desmaio",
    "desmaiei",
    "urgencia",
    "urgente",
    "emergencia",
    "muito sangue",
    "piorando",
    "piora rapida",
]

MEDICATION_CHANGE_KEYWORDS = [
    "devo tomar",
    "devo parar",
    "mudar dose",
    "mudar horario",
    "qual remedio",
    "qual medicamento",
]

MAYA_INSTRUCTIONS = (
    "Você é Maya, uma assistente virtual acolhedora de uma clínica de fertilidade. "
    "Responda sempre em português do Brasil, com linguagem simples, humana, calma e organizada. "
    "Seu papel é acompanhar a paciente com acolhimento, clareza e baixa carga cognitiva. "
    "Fale como uma companheira de jornada: valide o que a paciente sente, organize a resposta em passos curtos e ofereça continuidade de conversa. "
    "Você pode explicar etapas, ajudar a organizar a rotina e acolher emocionalmente. "
    "Evite soar técnica, fria ou burocrática. Use frases curtas e convites suaves como 'se quiser' ou 'podemos olhar juntas'. "
    "Não faça diagnóstico, não decida condutas clínicas, não personalize medicamentos e não substitua a equipe médica. "
    "Quando houver sintomas, risco clínico, urgência ou necessidade de decisão individual, acolha primeiro e oriente a falar com a equipe médica."
)


@dataclass
class MayaReply:
    answer: str
    mode: str
    intent: str
    risk_level: str
    suggested_next_step: str = ""


def normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text or "")
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(without_accents.lower().split())


def first_name_for(user) -> str:
    full_name = (user.full_name or "").strip()
    return full_name.split()[0] if full_name else "Você"


def ensure_default_conversations(user):
    conversations = []
    for kind, blueprint in CONVERSATION_BLUEPRINTS.items():
        conversation, _ = MayaConversation.objects.get_or_create(
            user=user,
            kind=kind,
            defaults={
                "title": blueprint["title"],
                "description": blueprint["description"],
                "starter_prompt": blueprint["starter_prompt"],
                "sort_order": blueprint["sort_order"],
            },
        )
        updates = []
        for field in ["title", "description", "starter_prompt", "sort_order"]:
            desired = blueprint[field]
            if getattr(conversation, field) != desired:
                setattr(conversation, field, desired)
                updates.append(field)
        if updates:
            updates.append("updated_at")
            conversation.save(update_fields=updates)
        conversations.append(conversation)
    return sorted(conversations, key=lambda item: (item.sort_order, item.id))


def get_conversation_or_default(user, conversation_kind: str | None = None):
    conversations = ensure_default_conversations(user)
    backfill_legacy_interactions(user, conversations)
    if conversation_kind:
        for conversation in conversations:
            if conversation.kind == conversation_kind:
                return conversation
    for conversation in conversations:
        if conversation.kind == MayaConversation.Kind.TREATMENT:
            return conversation
    return conversations[0]


def backfill_legacy_interactions(user, conversations=None):
    legacy_interactions = AIInteraction.objects.filter(user=user, conversation__isnull=True)
    if not legacy_interactions.exists():
        return

    conversations = conversations or ensure_default_conversations(user)
    conversation_map = {conversation.kind: conversation for conversation in conversations}
    for interaction in legacy_interactions:
        normalized = normalize_text(interaction.question)
        inferred_kind = infer_conversation_kind(normalized)
        intent, risk_level = classify_question(normalized, inferred_kind)
        interaction.conversation = conversation_map[inferred_kind]
        interaction.intent = intent
        interaction.risk_level = risk_level
        interaction.save(update_fields=["conversation", "intent", "risk_level"])


def get_prompt_examples(conversation_kind: str) -> list[str]:
    return CONVERSATION_BLUEPRINTS[conversation_kind]["examples"]


def get_conversation_empty_state(conversation_kind: str) -> dict[str, str]:
    blueprint = CONVERSATION_BLUEPRINTS[conversation_kind]
    return {
        "title": blueprint["empty_title"],
        "copy": blueprint["empty_copy"],
    }


def answer_question_with_maya(user, question: str, conversation: MayaConversation) -> AIInteraction:
    question = question.strip()
    if not question:
        raise ValidationError("Escreva sua dúvida antes de enviar.")

    normalized_question = normalize_text(question)
    intent, risk_level = classify_question(normalized_question, conversation.kind)

    if intent == AIInteraction.Intent.SYMPTOM:
        reply = build_symptom_reply(normalized_question, risk_level, user)
    else:
        reply = answer_with_llm_or_fallback(
            question=question,
            normalized_question=normalized_question,
            user=user,
            conversation=conversation,
            intent=intent,
            risk_level=risk_level,
        )

    return AIInteraction.objects.create(
        user=user,
        conversation=conversation,
        question=question,
        answer=reply.answer,
        mode=reply.mode,
        intent=reply.intent,
        risk_level=reply.risk_level,
        suggested_next_step=reply.suggested_next_step,
    )


def infer_conversation_kind(normalized_question: str) -> str:
    intent, _risk_level = classify_question(normalized_question, MayaConversation.Kind.TREATMENT)
    if intent == AIInteraction.Intent.ROUTINE:
        return MayaConversation.Kind.ROUTINE
    if intent in {AIInteraction.Intent.FEELINGS, AIInteraction.Intent.SYMPTOM}:
        return MayaConversation.Kind.FEELINGS
    return MayaConversation.Kind.TREATMENT


def classify_question(normalized_question: str, conversation_kind: str) -> tuple[str, str]:
    high_risk = any(keyword in normalized_question for keyword in HIGH_RISK_KEYWORDS)
    symptom_change = any(keyword in normalized_question for keyword in MEDICATION_CHANGE_KEYWORDS)
    symptom_signal = any(keyword in normalized_question for keyword in SYMPTOM_KEYWORDS)

    if high_risk or symptom_change:
        return AIInteraction.Intent.SYMPTOM, AIInteraction.RiskLevel.HIGH
    if symptom_signal:
        return AIInteraction.Intent.SYMPTOM, AIInteraction.RiskLevel.MEDIUM

    if any(keyword in normalized_question for keyword in FEELINGS_KEYWORDS):
        return AIInteraction.Intent.FEELINGS, AIInteraction.RiskLevel.LOW
    if any(keyword in normalized_question for keyword in ROUTINE_KEYWORDS):
        return AIInteraction.Intent.ROUTINE, AIInteraction.RiskLevel.LOW
    if any(keyword in normalized_question for keyword in TREATMENT_KEYWORDS):
        return AIInteraction.Intent.TREATMENT, AIInteraction.RiskLevel.LOW

    if conversation_kind == MayaConversation.Kind.FEELINGS:
        return AIInteraction.Intent.FEELINGS, AIInteraction.RiskLevel.LOW
    if conversation_kind == MayaConversation.Kind.ROUTINE:
        return AIInteraction.Intent.ROUTINE, AIInteraction.RiskLevel.LOW
    if conversation_kind == MayaConversation.Kind.TREATMENT:
        return AIInteraction.Intent.TREATMENT, AIInteraction.RiskLevel.LOW
    return AIInteraction.Intent.GENERAL, AIInteraction.RiskLevel.LOW


def answer_with_llm_or_fallback(question: str, normalized_question: str, user, conversation, intent: str, risk_level: str) -> MayaReply:
    if settings.MAYA_OPENAI_API_KEY and settings.MAYA_OPENAI_MODEL:
        try:
            answer = call_openai(question, user, conversation, intent, risk_level)
            return MayaReply(
                answer=answer,
                mode=AIInteraction.Mode.LLM,
                intent=intent,
                risk_level=risk_level,
                suggested_next_step=suggested_next_step_for_intent(user, conversation.kind, intent, risk_level),
            )
        except Exception:
            pass
    return fallback_reply(normalized_question, user, conversation.kind, intent, risk_level)


def fallback_reply(normalized_question: str, user, conversation_kind: str, intent: str, risk_level: str) -> MayaReply:
    if intent == AIInteraction.Intent.FEELINGS:
        return build_feelings_reply(user)
    if intent == AIInteraction.Intent.ROUTINE:
        return build_routine_reply(normalized_question, user)
    if intent == AIInteraction.Intent.TREATMENT:
        return build_treatment_reply(normalized_question, user)
    return build_general_reply(user, conversation_kind)


def build_symptom_reply(normalized_question: str, risk_level: str, user) -> MayaReply:
    name = first_name_for(user)
    if risk_level == AIInteraction.RiskLevel.HIGH:
        return MayaReply(
            answer=(
                f"{name}, sinto muito que isso esteja acontecendo. Eu não consigo avaliar sintomas clinicamente por aqui, "
                "então o mais seguro é falar com sua equipe médica agora. "
                "Se houver piora rápida, sangramento importante, falta de ar ou algo muito intenso, procure atendimento imediato. "
                "Se quiser, eu posso te ajudar a organizar a mensagem para a clínica."
            ),
            mode=AIInteraction.Mode.FALLBACK,
            intent=AIInteraction.Intent.SYMPTOM,
            risk_level=risk_level,
            suggested_next_step="Avise a equipe médica agora e conte quando começou, a intensidade e se houve outros sinais.",
        )

    symptom_name = "esse sintoma" if "dor" not in normalized_question else "essa dor"
    return MayaReply(
        answer=(
            f"{name}, sinto muito que você esteja sentindo {symptom_name}. Eu não consigo avaliar sintomas clinicamente por aqui, "
            "mas o mais seguro é avisar sua equipe médica para receber uma orientação individual. "
            "Se quiser, eu fico com você nessa parte e posso te ajudar a organizar o que contar para a clínica."
        ),
        mode=AIInteraction.Mode.FALLBACK,
        intent=AIInteraction.Intent.SYMPTOM,
        risk_level=risk_level,
        suggested_next_step="Anote quando começou, a intensidade e se apareceram outros sinais antes de falar com a equipe.",
    )


def build_feelings_reply(user) -> MayaReply:
    name = first_name_for(user)
    anchor = build_support_anchor(user)
    return MayaReply(
        answer=(
            f"{name}, sinto muito que este momento esteja pesado. Você não precisa dar conta de tudo agora. "
            "Vamos por partes. O tratamento pode mexer com o corpo e com as emoções ao mesmo tempo, e isso não significa fraqueza. "
            f"{anchor} Se quiser, eu continuo aqui com você e podemos olhar uma coisa de cada vez."
        ),
        mode=AIInteraction.Mode.FALLBACK,
        intent=AIInteraction.Intent.FEELINGS,
        risk_level=AIInteraction.RiskLevel.LOW,
        suggested_next_step="Escolha só um próximo passo pequeno agora. Se quiser, continue me contando o que está pesando mais.",
    )


def build_routine_reply(normalized_question: str, user) -> MayaReply:
    today = timezone.localdate()
    doses_today = Medication.objects.filter(patient=user, scheduled_for__date=today).order_by("scheduled_for")
    pending_dose = doses_today.filter(status=Medication.Status.PENDING).first()
    upcoming_appointment = Appointment.objects.filter(
        patient=user,
        scheduled_at__date__gte=today,
    ).order_by("scheduled_at").first()

    if any(keyword in normalized_question for keyword in ["agenda", "consulta", "exame", "compromisso"]):
        if upcoming_appointment:
            answer = (
                "Você não precisa organizar o dia inteiro de uma vez. Vamos olhar só o que vem primeiro. "
                f"No momento, o próximo compromisso é {upcoming_appointment.get_type_display().lower()} "
                f"em {timezone.localtime(upcoming_appointment.scheduled_at).strftime('%d/%m às %H:%M')}. "
                "Depois disso, se quiser, eu posso te ajudar a revisar o resto com calma."
            )
        else:
            answer = (
                "Podemos deixar isso bem leve. A agenda foi pensada para mostrar consultas e exames por ordem de data, "
                "então você pode olhar só o próximo compromisso quando ele aparecer."
            )
        return MayaReply(
            answer=answer,
            mode=AIInteraction.Mode.FALLBACK,
            intent=AIInteraction.Intent.ROUTINE,
            risk_level=AIInteraction.RiskLevel.LOW,
            suggested_next_step="Abra sua agenda e olhe apenas o próximo compromisso. Se quiser, depois voltamos para o restante.",
        )

    if doses_today.exists():
        total_doses = doses_today.count()
        pending_sentence = (
            f"A próxima dose pendente é {pending_dose.name} às {timezone.localtime(pending_dose.scheduled_for).strftime('%H:%M')}."
            if pending_dose
            else "As doses de hoje já foram registradas no aplicativo."
        )
        answer = (
            "Para ficar mais leve, vamos olhar só a próxima dose primeiro e deixar o resto para depois. "
            f"Hoje há {total_doses} dose{'s' if total_doses != 1 else ''} programada{'s' if total_doses != 1 else ''}. {pending_sentence} "
            "Se a dúvida for sobre mudar dose, horário ou uso, fale com a equipe médica."
        )
    else:
        answer = (
            "Podemos simplificar isso juntas. Olhe primeiro o que precisa acontecer hoje e depois o que vem a seguir. "
            "Quando houver medicações cadastradas, a rotina do aplicativo ajuda a acompanhar tudo sem exigir que você segure tudo de cabeça."
        )
    return MayaReply(
        answer=answer,
        mode=AIInteraction.Mode.FALLBACK,
        intent=AIInteraction.Intent.ROUTINE,
        risk_level=AIInteraction.RiskLevel.LOW,
        suggested_next_step="Comece pela próxima dose ou pelo próximo compromisso do dia. Se quiser, eu posso seguir com você depois disso.",
    )


def build_treatment_reply(normalized_question: str, user) -> MayaReply:
    treatment = Treatment.objects.filter(patient=user, is_active=True).prefetch_related("steps").first()
    current_step = treatment.current_step if treatment else None
    next_step = treatment.next_step if treatment else None

    if "coleta" in normalized_question:
        answer = (
            "Depois da coleta, os óvulos seguem para o laboratório e os embriões passam a ser acompanhados pela equipe médica. "
            "Se quiser, eu também posso te explicar o que costuma vir depois dessa etapa."
        )
    elif any(keyword in normalized_question for keyword in ["embriao", "embrioes", "fertilizacao"]):
        answer = (
            "Depois da fertilização, os embriões são observados pela equipe para entender a evolução de cada etapa. "
            "Podemos olhar isso juntas com calma, uma fase por vez."
        )
    elif "transferencia" in normalized_question:
        answer = (
            "Na transferência, o embrião é colocado no útero em um momento planejado pela equipe médica. "
            "Se quiser, eu posso te contar também o que costuma acontecer antes e depois dessa fase."
        )
    elif any(keyword in normalized_question for keyword in ["proximo passo", "proxima etapa", "o que vem depois", "o que vem a seguir"]):
        if next_step:
            answer = (
                f"Vamos olhar só o próximo passo. De forma geral, ele costuma ser {next_step.name.lower()}. "
                "Ele aparece na timeline para ajudar você a acompanhar o caminho com mais previsibilidade."
            )
        elif current_step:
            answer = (
                f"No momento, a etapa em destaque é {current_step.name.lower()}. "
                "Quando houver uma nova atualização do tratamento, o próximo passo vai aparecer na timeline e eu posso te ajudar a entender essa mudança."
            )
        else:
            answer = "As etapas do tratamento já estão organizadas. Assim que a primeira começar, o próximo passo ficará mais claro e visível para você."
    elif current_step:
        answer = (
            f"Hoje a etapa em destaque é {current_step.name.lower()}. "
            "Se quiser, eu posso continuar com você nessa fase e explicar o que costuma acontecer agora ou no passo seguinte."
        )
    else:
        answer = (
            "Posso te acompanhar com uma visão geral do tratamento. "
            "Se quiser, começamos pela etapa atual ou pelo que costuma vir depois."
        )

    return MayaReply(
        answer=answer,
        mode=AIInteraction.Mode.FALLBACK,
        intent=AIInteraction.Intent.TREATMENT,
        risk_level=AIInteraction.RiskLevel.LOW,
        suggested_next_step="Abra a timeline para ver a etapa atual e o próximo passo lado a lado. Se quiser, eu posso te explicar cada um deles.",
    )


def build_general_reply(user, conversation_kind: str) -> MayaReply:
    if conversation_kind == MayaConversation.Kind.FEELINGS:
        return build_feelings_reply(user)
    if conversation_kind == MayaConversation.Kind.ROUTINE:
        return build_routine_reply("", user)
    return build_treatment_reply("", user)


def build_support_anchor(user) -> str:
    next_dose = Medication.objects.filter(
        patient=user,
        scheduled_for__date=timezone.localdate(),
        status=Medication.Status.PENDING,
    ).order_by("scheduled_for").first()
    if next_dose:
        return (
            f"Se ajudar, podemos começar só pela próxima dose de {next_dose.name} "
            f"às {timezone.localtime(next_dose.scheduled_for).strftime('%H:%M')}."
        )

    next_appointment = Appointment.objects.filter(
        patient=user,
        scheduled_at__date__gte=timezone.localdate(),
    ).order_by("scheduled_at").first()
    if next_appointment:
        return (
            "Talvez o passo mais concreto de agora seja revisar "
            f"{next_appointment.get_type_display().lower()} em {timezone.localtime(next_appointment.scheduled_at).strftime('%d/%m às %H:%M')}."
        )

    treatment = Treatment.objects.filter(patient=user, is_active=True).prefetch_related("steps").first()
    if treatment and treatment.next_step:
        return f"Se quiser, podemos olhar só a próxima etapa: {treatment.next_step.name.lower()}."

    return "Podemos ir por partes e olhar apenas o próximo passo concreto do seu dia."


def suggested_next_step_for_intent(user, conversation_kind: str, intent: str, risk_level: str) -> str:
    if intent == AIInteraction.Intent.SYMPTOM:
        return "Avise sua equipe médica e conte quando começou, a intensidade e se houve outros sinais. Se quiser, eu posso te ajudar a organizar essa mensagem."
    if intent == AIInteraction.Intent.FEELINGS:
        return "Escolha só um próximo passo pequeno agora. Se quiser, continue me contando o que está pesando mais."
    if intent == AIInteraction.Intent.ROUTINE:
        return "Olhe primeiro a próxima dose ou o próximo compromisso. Depois, se quiser, voltamos para o restante."
    if intent == AIInteraction.Intent.TREATMENT:
        return "Confira a timeline para ver a etapa atual e o que vem depois. Se quiser, eu posso te explicar cada parte."
    return "Siga por partes e, se quiser, me conte um pouco mais para eu te acompanhar melhor."


def build_safe_context_summary(user) -> str:
    treatment = Treatment.objects.filter(patient=user, is_active=True).prefetch_related("steps").first()
    current_step = treatment.current_step.name if treatment and treatment.current_step else "Sem etapa em andamento"
    next_step = treatment.next_step.name if treatment and treatment.next_step else "Sem próxima etapa definida"
    next_dose = Medication.objects.filter(
        patient=user,
        scheduled_for__date=timezone.localdate(),
        status=Medication.Status.PENDING,
    ).order_by("scheduled_for").first()
    next_appointment = Appointment.objects.filter(
        patient=user,
        scheduled_at__date__gte=timezone.localdate(),
    ).order_by("scheduled_at").first()
    dose_text = (
        f"{next_dose.name} às {timezone.localtime(next_dose.scheduled_for).strftime('%H:%M')}"
        if next_dose
        else "Sem dose pendente hoje"
    )
    appointment_text = (
        f"{next_appointment.get_type_display()} em {timezone.localtime(next_appointment.scheduled_at).strftime('%d/%m às %H:%M')}"
        if next_appointment
        else "Sem compromisso próximo"
    )
    return (
        f"Etapa atual: {current_step}. "
        f"Próximo passo: {next_step}. "
        f"Próxima dose: {dose_text}. "
        f"Próximo compromisso: {appointment_text}."
    )


def build_recent_history(conversation: MayaConversation) -> str:
    recent_messages = conversation.interactions.order_by("-created_at")[:3]
    if not recent_messages:
        return "Sem histórico recente nessa conversa."
    lines = []
    for interaction in reversed(list(recent_messages)):
        lines.append(f"Paciente: {interaction.question}")
        lines.append(f"Maya: {interaction.answer}")
    return "\n".join(lines)


def call_openai(question: str, user, conversation: MayaConversation, intent: str, risk_level: str) -> str:
    payload = {
        "model": settings.MAYA_OPENAI_MODEL,
        "instructions": MAYA_INSTRUCTIONS,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"Conversa selecionada: {conversation.title}\n"
                            f"Descrição da conversa: {conversation.description}\n"
                            f"Intenção detectada: {intent}\n"
                            f"Nível de risco: {risk_level}\n"
                            f"Contexto seguro: {build_safe_context_summary(user)}\n"
                            f"Histórico recente:\n{build_recent_history(conversation)}\n"
                            f"Pergunta atual: {question}"
                        ),
                    }
                ],
            }
        ],
    }
    http_request = urllib_request.Request(
        settings.MAYA_OPENAI_BASE_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.MAYA_OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib_request.urlopen(http_request, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    if data.get("output_text"):
        return data["output_text"]
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                return content.get("text", "")
    raise error.HTTPError(settings.MAYA_OPENAI_BASE_URL, 500, "Resposta inválida da Maya", hdrs=None, fp=None)
