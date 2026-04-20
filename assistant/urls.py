from django.urls import path

from .views import MayaChatView, MayaSendMessageView


app_name = "assistant"

urlpatterns = [
    path("maya/", MayaChatView.as_view(), name="chat"),
    path("maya/send/", MayaSendMessageView.as_view(), name="send"),
    path("maya/<slug:conversation_kind>/", MayaChatView.as_view(), name="chat-kind"),
]
