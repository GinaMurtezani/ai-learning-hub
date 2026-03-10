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


class LessonWithProgressSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "slug",
            "title",
            "description",
            "xp_reward",
            "order",
            "completed",
            "completed_at",
        ]

    def _get_progress(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        return (
            LessonProgress.objects.filter(
                user=request.user,
                lesson=obj,
                completed=True,
            )
            .first()
        )

    def get_completed(self, obj):
        return self._get_progress(obj) is not None

    def get_completed_at(self, obj):
        progress = self._get_progress(obj)
        return progress.completed_at if progress else None


class LearningPathListSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    completed_count = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    total_xp = serializers.SerializerMethodField()
    lessons = LessonWithProgressSerializer(many=True, read_only=True)

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
            "total_xp",
            "lessons",
        ]

    def get_total_xp(self, obj):
        return sum(l.xp_reward for l in obj.lessons.all())

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
