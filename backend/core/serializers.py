from django.contrib.auth.models import User
from rest_framework import serializers

from lessons.models import LessonProgress

from .models import Achievement, UserAchievement, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "xp",
            "level",
            "streak_days",
            "last_activity",
            "avatar_color",
        ]
        read_only_fields = ["user", "xp", "level", "streak_days", "last_activity"]


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "icon",
            "xp_reward",
            "requirement_type",
            "requirement_value",
        ]


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ["id", "achievement", "unlocked_at"]


class AchievementWithUnlockSerializer(serializers.ModelSerializer):
    unlocked = serializers.SerializerMethodField()
    unlocked_at = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "icon",
            "xp_reward",
            "requirement_type",
            "requirement_value",
            "unlocked",
            "unlocked_at",
            "progress",
        ]

    def _get_user(self):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return request.user
        return None

    def get_unlocked(self, obj):
        user = self._get_user()
        if not user:
            return False
        return obj.userachievement_set.filter(user=user).exists()

    def get_unlocked_at(self, obj):
        user = self._get_user()
        if not user:
            return None
        ua = obj.userachievement_set.filter(user=user).first()
        return ua.unlocked_at if ua else None

    def get_progress(self, obj):
        user = self._get_user()
        target = obj.requirement_value
        if not user:
            return {"current": 0, "target": target}

        current = 0
        if obj.requirement_type == "lessons_completed":
            current = LessonProgress.objects.filter(
                user=user, completed=True
            ).count()
        elif obj.requirement_type == "xp_total":
            current = user.profile.xp
        elif obj.requirement_type == "streak":
            current = user.profile.streak_days
        elif obj.requirement_type == "first_chat":
            current = 1 if user.chat_messages.exists() else 0

        return {"current": min(current, target), "target": target}


class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "display_name",
            "xp",
            "level",
            "streak_days",
            "avatar_color",
        ]

    def get_display_name(self, obj):
        u = obj.user
        full = f"{u.first_name} {u.last_name}".strip()
        return full or u.username
