from datetime import timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import ChatAgent, ChatMessage
from lessons.models import LearningPath, LessonProgress

from .models import Achievement, UserAchievement, UserProfile
from .serializers import (
    AchievementWithUnlockSerializer,
    LeaderboardSerializer,
    UserProfileSerializer,
)


class ProfileView(RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class LeaderboardView(ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return UserProfile.objects.select_related("user").order_by("-xp")[:20]


class AchievementsView(ListAPIView):
    serializer_class = AchievementWithUnlockSerializer
    permission_classes = [IsAuthenticated]
    queryset = Achievement.objects.all()


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"error": "Username and password required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        return Response({"username": user.username, "id": user.id})


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "overview": self._overview(),
                "xp_distribution": self._xp_distribution(),
                "popular_lessons": self._popular_lessons(),
                "path_progress": self._path_progress(),
                "activity_last_7_days": self._activity_last_7_days(),
                "achievements_summary": self._achievements_summary(),
                "chat_stats": self._chat_stats(),
            }
        )

    def _overview(self):
        total_users = User.objects.count()
        today = timezone.now().date()
        active_today = UserProfile.objects.filter(
            last_activity__date=today
        ).count()
        total_completed = LessonProgress.objects.filter(completed=True).count()
        total_messages = ChatMessage.objects.count()
        total_xp = sum(UserProfile.objects.values_list("xp", flat=True))
        avg_level_raw = UserProfile.objects.aggregate(a=Avg("level"))["a"]
        avg_level = round(avg_level_raw, 1) if avg_level_raw else 0

        return {
            "total_users": total_users,
            "active_users_today": active_today,
            "total_lessons_completed": total_completed,
            "total_chat_messages": total_messages,
            "total_xp_earned": total_xp,
            "average_level": avg_level,
        }

    def _xp_distribution(self):
        profiles = UserProfile.objects.values_list("xp", flat=True)
        ranges = [
            ("0-99", 0, 99),
            ("100-199", 100, 199),
            ("200-299", 200, 299),
            ("300-399", 300, 399),
            ("400-499", 400, 499),
        ]
        result = []
        for label, lo, hi in ranges:
            count = sum(1 for xp in profiles if lo <= xp <= hi)
            result.append({"range": label, "count": count})
        result.append(
            {"range": "500+", "count": sum(1 for xp in profiles if xp >= 500)}
        )
        return result

    def _popular_lessons(self):
        from lessons.models import Lesson

        lessons = (
            Lesson.objects.annotate(
                completions=Count(
                    "progress", filter=Q(progress__completed=True)
                ),
                message_count=Count("chat_messages"),
            )
            .select_related("path")
            .order_by("-completions", "-message_count")[:5]
        )
        return [
            {
                "title": l.title,
                "path_title": l.path.title,
                "completions": l.completions,
                "chat_messages": l.message_count,
            }
            for l in lessons
        ]

    def _path_progress(self):
        paths = LearningPath.objects.prefetch_related("lessons").all()
        total_users = User.objects.count()
        result = []
        for path in paths:
            total_lessons = path.lessons.count()
            if total_lessons == 0 or total_users == 0:
                avg_pct = 0
            else:
                total_completed = LessonProgress.objects.filter(
                    lesson__path=path, completed=True
                ).count()
                # average completion across all users
                avg_pct = round(
                    total_completed / (total_lessons * total_users) * 100
                )
            result.append(
                {
                    "title": path.title,
                    "icon": path.icon,
                    "total_lessons": total_lessons,
                    "avg_completion_percent": avg_pct,
                }
            )
        return result

    def _activity_last_7_days(self):
        today = timezone.now().date()
        result = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            lessons_done = LessonProgress.objects.filter(
                completed=True, completed_at__date=day
            ).count()
            messages = ChatMessage.objects.filter(
                created_at__date=day
            ).count()
            result.append(
                {
                    "date": day.isoformat(),
                    "lessons_completed": lessons_done,
                    "chat_messages": messages,
                }
            )
        return result

    def _achievements_summary(self):
        total = Achievement.objects.count()
        if total == 0:
            return {
                "total": 0,
                "unlocked_by_anyone": 0,
                "most_common": None,
                "rarest": None,
            }

        achievements = Achievement.objects.annotate(
            unlock_count=Count("userachievement")
        )
        unlocked_by_anyone = achievements.filter(unlock_count__gt=0).count()

        most_common = achievements.order_by("-unlock_count", "name").first()
        rarest = achievements.order_by("unlock_count", "name").first()

        return {
            "total": total,
            "unlocked_by_anyone": unlocked_by_anyone,
            "most_common": {
                "name": most_common.name,
                "icon": most_common.icon,
                "unlock_count": most_common.unlock_count,
            },
            "rarest": {
                "name": rarest.name,
                "icon": rarest.icon,
                "unlock_count": rarest.unlock_count,
            },
        }

    def _chat_stats(self):
        total_messages = ChatMessage.objects.count()
        lessons_with_chat = (
            ChatMessage.objects.exclude(lesson=None)
            .values("lesson")
            .distinct()
            .count()
        )
        avg_per_lesson = (
            round(total_messages / lessons_with_chat, 1)
            if lessons_with_chat > 0
            else 0
        )

        # Most active lesson
        from lessons.models import Lesson

        most_active_qs = (
            Lesson.objects.annotate(msg_count=Count("chat_messages"))
            .filter(msg_count__gt=0)
            .order_by("-msg_count")
            .first()
        )
        most_active = None
        if most_active_qs:
            most_active = {
                "title": most_active_qs.title,
                "message_count": most_active_qs.msg_count,
            }

        # Agent usage — agents exist but ChatMessage has no agent FK,
        # so we list agents without per-message breakdown
        agents = ChatAgent.objects.all()
        agent_usage = [
            {"agent": a.name, "icon": a.icon, "messages": 0} for a in agents
        ]

        return {
            "total_messages": total_messages,
            "avg_messages_per_lesson": avg_per_lesson,
            "most_active_lesson": most_active,
            "agent_usage": agent_usage,
        }


class EmailPreviewView(APIView):
    """Preview email templates in browser. Only available in DEBUG mode."""

    permission_classes = [AllowAny]

    def get(self, request, template_name):
        from django.conf import settings as django_settings
        from django.http import HttpResponse

        if not django_settings.DEBUG:
            return Response(
                {"error": "Only available in DEBUG mode."},
                status=status.HTTP_403_FORBIDDEN,
            )

        from core.emails import get_preview_html

        html = get_preview_html(template_name)
        if html is None:
            return Response(
                {
                    "error": f"Unknown template: {template_name}",
                    "available": [
                        "welcome",
                        "achievement",
                        "level-up",
                        "path-completed",
                        "streak-reminder",
                    ],
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return HttpResponse(html, content_type="text/html")


DEMO_ROLES = {
    "demo": "Lernende",
    "anna": "Top-Lernende",
    "marco": "Fortgeschritten",
}


class DemoUsersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        demo_usernames = list(DEMO_ROLES.keys())
        profiles = UserProfile.objects.select_related("user").filter(
            user__username__in=demo_usernames
        )
        result = []
        for profile in profiles:
            user = profile.user
            result.append(
                {
                    "username": user.username,
                    "display_name": f"{user.first_name} {user.last_name}",
                    "avatar_color": profile.avatar_color,
                    "role": DEMO_ROLES.get(user.username, "Lernende"),
                }
            )
        return Response(result)
