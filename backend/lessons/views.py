from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.certificates import generate_certificate
from core.models import Achievement, UserAchievement
from core.serializers import UserAchievementSerializer, UserProfileSerializer

from .models import Lesson, LearningPath, LessonProgress
from .serializers import (
    LearningPathListSerializer,
    LessonSerializer,
)


class LearningPathListView(ListAPIView):
    serializer_class = LearningPathListSerializer
    permission_classes = [IsAuthenticated]
    queryset = LearningPath.objects.all()


class LearningPathDetailView(RetrieveAPIView):
    serializer_class = LearningPathListSerializer
    permission_classes = [IsAuthenticated]
    queryset = LearningPath.objects.prefetch_related("lessons")
    lookup_field = "slug"


class LessonDetailView(RetrieveAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    queryset = Lesson.objects.all()
    lookup_field = "slug"


class LessonCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        try:
            lesson = Lesson.objects.get(slug=slug)
        except Lesson.DoesNotExist:
            return Response(
                {"error": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND
            )

        progress, created = LessonProgress.objects.get_or_create(
            user=request.user, lesson=lesson
        )

        # Already completed — no double XP
        if progress.completed:
            return Response(
                {
                    "profile": UserProfileSerializer(request.user.profile).data,
                    "new_achievements": [],
                    "already_completed": True,
                }
            )

        # Mark completed
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

        # Award XP and recalculate level
        profile = request.user.profile
        old_level = profile.level
        profile.xp += lesson.xp_reward
        profile.level = profile.xp // 100 + 1
        profile.save()

        # Level-up email
        if profile.level > old_level:
            from core.emails import send_level_up_email

            send_level_up_email(request.user, profile.level, profile.xp)

        # Check achievements
        new_achievements = self._check_achievements(request.user)

        # Check if entire path is now completed
        path = lesson.path
        total_lessons = path.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            user=request.user, lesson__path=path, completed=True
        ).count()
        if completed_lessons == total_lessons:
            from core.emails import send_path_completed_email

            send_path_completed_email(request.user, path)

        return Response(
            {
                "profile": UserProfileSerializer(profile).data,
                "new_achievements": UserAchievementSerializer(
                    new_achievements, many=True
                ).data,
                "already_completed": False,
            }
        )

    def _check_achievements(self, user):
        unlocked = []
        completed_count = LessonProgress.objects.filter(
            user=user, completed=True
        ).count()
        profile = user.profile

        for achievement in Achievement.objects.all():
            # Skip already unlocked
            if UserAchievement.objects.filter(
                user=user, achievement=achievement
            ).exists():
                continue

            earned = False
            if achievement.requirement_type == "lessons_completed":
                earned = completed_count >= achievement.requirement_value
            elif achievement.requirement_type == "xp_total":
                earned = profile.xp >= achievement.requirement_value
            elif achievement.requirement_type == "streak":
                earned = profile.streak_days >= achievement.requirement_value
            elif achievement.requirement_type == "first_chat":
                earned = user.chat_messages.exists()

            if earned:
                ua = UserAchievement.objects.create(
                    user=user, achievement=achievement
                )
                unlocked.append(ua)
                from core.emails import send_achievement_email

                send_achievement_email(user, achievement)

        return unlocked


class CertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        path = get_object_or_404(LearningPath, slug=slug)
        lessons = path.lessons.all()
        completed = LessonProgress.objects.filter(
            user=request.user,
            lesson__in=lessons,
            completed=True,
        )

        if completed.count() < lessons.count():
            remaining = lessons.count() - completed.count()
            return Response(
                {
                    "error": f"Lernpfad noch nicht abgeschlossen. "
                    f"Noch {remaining} Lektionen offen.",
                    "completed": completed.count(),
                    "total": lessons.count(),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Letztes Completion-Datum
        last_completed = completed.order_by("-completed_at").first()
        completed_date = last_completed.completed_at if last_completed else None

        pdf_buffer = generate_certificate(request.user, path, completed_date)

        filename = (
            f"Zertifikat_{path.title.replace(' ', '_')}_{request.user.username}.pdf"
        )
        response = HttpResponse(pdf_buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
