from rest_framework import serializers

from .models import Lesson, LearningPath, LessonProgress


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "slug",
            "title",
            "description",
            "content",
            "xp_reward",
            "order",
            "ai_system_prompt",
        ]


class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "slug", "title", "description", "xp_reward", "order"]


class LearningPathSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)

    class Meta:
        model = LearningPath
        fields = [
            "id",
            "slug",
            "title",
            "description",
            "icon",
            "difficulty",
            "order",
            "lessons",
        ]


class LearningPathListSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    completed_count = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = LearningPath
        fields = [
            "id",
            "slug",
            "title",
            "description",
            "icon",
            "difficulty",
            "order",
            "lessons_count",
            "completed_count",
            "progress_percent",
        ]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_completed_count(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0
        return LessonProgress.objects.filter(
            user=request.user,
            lesson__path=obj,
            completed=True,
        ).count()

    def get_progress_percent(self, obj):
        total = obj.lessons.count()
        if total == 0:
            return 0
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0
        completed = LessonProgress.objects.filter(
            user=request.user,
            lesson__path=obj,
            completed=True,
        ).count()
        return round(completed / total * 100)


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ["id", "lesson", "user", "completed", "completed_at"]
