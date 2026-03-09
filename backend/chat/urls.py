from django.urls import path

from . import views

urlpatterns = [
    path("chat/", views.ChatView.as_view(), name="chat"),
    path("chat/agents/", views.ChatAgentListView.as_view(), name="chat-agents"),
]
