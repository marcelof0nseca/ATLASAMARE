from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from core.mixins import PatientRequiredMixin

from .services import (
    answer_question_with_maya,
    ensure_default_conversations,
    get_conversation_empty_state,
    get_conversation_or_default,
    get_prompt_examples,
)


class MayaChatView(PatientRequiredMixin, TemplateView):
    template_name = "patient/maya.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversations = ensure_default_conversations(self.request.user)
        selected_conversation = get_conversation_or_default(
            self.request.user,
            self.kwargs.get("conversation_kind"),
        )
        recent_interactions = list(selected_conversation.interactions.order_by("-created_at")[:12])[::-1]
        context.update(
            {
                "conversations": conversations,
                "selected_conversation": selected_conversation,
                "interactions": recent_interactions,
                "prompt_examples": get_prompt_examples(selected_conversation.kind),
                "empty_state": get_conversation_empty_state(selected_conversation.kind),
                "active_nav": "maya",
            }
        )
        return context


class MayaSendMessageView(PatientRequiredMixin, View):
    def post(self, request):
        question = request.POST.get("question", "").strip()
        conversation = get_conversation_or_default(
            request.user,
            request.POST.get("conversation_kind"),
        )
        try:
            interaction = answer_question_with_maya(
                user=request.user,
                question=question,
                conversation=conversation,
            )
        except ValidationError as exc:
            if request.headers.get("HX-Request") == "true":
                return render(
                    request,
                    "patient/partials/maya_exchange.html",
                    {
                        "interaction": {
                            "question": question or "Pergunta vazia",
                            "answer": exc.message,
                            "intent": "general",
                            "risk_level": "low",
                            "suggested_next_step": "",
                        }
                    },
                    status=400,
                )
            messages.error(request, exc.message)
            return redirect("assistant:chat-kind", conversation_kind=conversation.kind)

        if request.headers.get("HX-Request") == "true":
            return render(
                request,
                "patient/partials/maya_exchange.html",
                {"interaction": interaction},
            )

        messages.success(request, "A Maya respondeu com cuidado.")
        return redirect("assistant:chat-kind", conversation_kind=conversation.kind)
