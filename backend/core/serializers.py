from django.contrib.auth.models import User
from rest_framework import serializers

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
        ]

    def get_unlocked(self, obj):
        user = self.context.get("request")
        if user and hasattr(user, "user"):
            user = user.user
        if not user or not user.is_authenticated:
            return False
        return obj.userachievement_set.filter(user=user).exists()

    def get_unlocked_at(self, obj):
        user = self.context.get("request")
        if user and hasattr(user, "user"):
            user = user.user
        if not user or not user.is_authenticated:
            return None
        ua = obj.userachievement_set.filter(user=user).first()
        return ua.unlocked_at if ua else None


class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "username", "xp", "level", "avatar_color"]
