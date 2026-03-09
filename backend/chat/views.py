import os

from anthropic import Anthropic, APIError
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Achievement, UserAchievement
from lessons.models import Lesson

from .models import ChatAgent, ChatMessage
from .serializers import ChatAgentSerializer, ChatInputSerializer

DEFAULT_SYSTEM_PROMPT = (
    "Du bist ein freundlicher und hilfreicher AI-Tutor auf der AI Learning Hub "
    "Plattform. Du hilfst Lernenden dabei, Konzepte der K\u00fcnstlichen Intelligenz "
    "zu verstehen. Antworte auf Deutsch, sei ermutigend und verwende einfache "
    "Erkl\u00e4rungen mit Beispielen."
)


class ChatAgentListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ChatAgentSerializer
    queryset = ChatAgent.objects.all()


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.conf import settings as django_settings
        api_key = os.getenv("ANTHROPIC_API_KEY") or django_settings.ANTHROPIC_API_KEY
        if not api_key:
            return Response(
                {"error": "ANTHROPIC_API_KEY is not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = ChatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data["message"]
        lesson_id = serializer.validated_data.get("lesson_id")
        agent_slug = serializer.validated_data.get("agent_slug")

        # Resolve lesson and system prompt
        lesson = None
        system_prompt = DEFAULT_SYSTEM_PROMPT
        if lesson_id:
            try:
                lesson = Lesson.objects.get(id=lesson_id)
            except Lesson.DoesNotExist:
                return Response(
                    {"error": "Lesson not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if lesson.ai_system_prompt:
                system_prompt = lesson.ai_system_prompt

        # Agent overrides default prompt (but not lesson prompt)
        if agent_slug and not (lesson and lesson.ai_system_prompt):
            try:
                agent = ChatAgent.objects.get(slug=agent_slug)
                system_prompt = agent.system_prompt
            except ChatAgent.DoesNotExist:
                return Response(
                    {"error": "Agent not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Load conversation history (last 20 messages for this user+lesson)
        history = ChatMessage.objects.filter(
            user=request.user, lesson=lesson
        ).order_by("created_at")[:20]
        messages_history = [
            {"role": msg.role, "content": msg.content} for msg in history
        ]
        messages_history.append({"role": "user", "content": message})

        # Call Anthropic API
        try:
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system_prompt,
                messages=messages_history,
            )
            ai_response = response.content[0].text
        except APIError as e:
            return Response(
                {"error": f"Anthropic API error: {e}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Save messages
        ChatMessage.objects.create(
            user=request.user, lesson=lesson, role="user", content=message
        )
        ChatMessage.objects.create(
            user=request.user, lesson=lesson, role="assistant", content=ai_response
        )

        # Check first-chat achievement
        new_achievements = self._check_first_chat_achievement(request.user)

        return Response(
            {
                "response": ai_response,
                "lesson_id": lesson_id,
                "new_achievements": [
                    {
                        "name": ua.achievement.name,
                        "icon": ua.achievement.icon,
                        "xp_reward": ua.achievement.xp_reward,
                    }
                    for ua in new_achievements
                ],
            }
        )

    def _check_first_chat_achievement(self, user):
        unlocked = []
        for achievement in Achievement.objects.filter(requirement_type="first_chat"):
            if UserAchievement.objects.filter(
                user=user, achievement=achievement
            ).exists():
                continue
            ua = UserAchievement.objects.create(user=user, achievement=achievement)
            if achievement.xp_reward:
                profile = user.profile
                profile.xp += achievement.xp_reward
                profile.level = profile.xp // 100 + 1
                profile.save()
            unlocked.append(ua)
        return unlocked
