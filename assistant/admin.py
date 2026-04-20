from django.contrib import admin

from .models import AIInteraction, MayaConversation


@admin.register(MayaConversation)
class MayaConversationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "kind", "sort_order"]
    list_filter = ["kind"]
    search_fields = ["user__full_name", "title", "description"]


@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    list_display = ["user", "conversation", "intent", "risk_level", "mode", "created_at"]
    list_filter = ["conversation__kind", "intent", "risk_level", "mode"]
    search_fields = ["user__full_name", "question", "answer", "suggested_next_step"]
