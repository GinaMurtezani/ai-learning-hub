from rest_framework import serializers

from .models import ChatAgent, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "lesson", "role", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField()
    lesson_id = serializers.IntegerField(required=False)
    agent_slug = serializers.SlugField(required=False)


class ChatAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatAgent
        fields = ["slug", "name", "description", "icon", "color"]
