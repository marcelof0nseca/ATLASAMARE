from django.urls import path

from .api_views import AIInteractionListCreateAPIView, MayaConversationListAPIView


urlpatterns = [
    path("assistant/conversations", MayaConversationListAPIView.as_view(), name="api-assistant-conversations"),
    path("assistant/interactions", AIInteractionListCreateAPIView.as_view(), name="api-assistant-interactions"),
]
