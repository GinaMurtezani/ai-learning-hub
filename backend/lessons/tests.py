import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Achievement, UserAchievement
from lessons.models import Lesson, LearningPath, LessonProgress


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="otheruser", password="testpass123")


@pytest.fixture
def learning_path(db):
    return LearningPath.objects.create(
        slug="ai-basics",
        title="AI Grundlagen",
        description="Lerne die Grundlagen der KI",
        icon="\U0001F9E0",
        difficulty="beginner",
        order=1,
    )


@pytest.fixture
def other_path(db):
    return LearningPath.objects.create(
        slug="prompt-eng",
        title="Prompt Engineering",
        description="Lerne Prompt Engineering",
        icon="\u270D\uFE0F",
        difficulty="intermediate",
        order=2,
    )


@pytest.fixture
def lesson(learning_path):
    return Lesson.objects.create(
        path=learning_path,
        slug="intro-ai",
        title="Intro to AI",
        description="First lesson",
        content="# Welcome",
        ai_system_prompt="You are a helpful tutor.",
        xp_reward=10,
        order=1,
    )


@pytest.fixture
def other_lesson(learning_path):
    return Lesson.objects.create(
        path=learning_path,
        slug="history-ai",
        title="History of AI",
        xp_reward=15,
        order=2,
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


# ── LearningPath Model ──────────────────────────────────────


class TestLearningPath:
    def test_create(self, learning_path):
        assert learning_path.pk is not None

    def test_str_returns_title(self, learning_path):
        assert str(learning_path) == "AI Grundlagen"

    def test_slug_unique(self, learning_path):
        with pytest.raises(IntegrityError):
            LearningPath.objects.create(
                slug="ai-basics", title="Dup", description="D", icon="X", difficulty="beginner"
            )

    def test_default_order(self, db):
        lp = LearningPath.objects.create(
            slug="no-order", title="No Order", description="D", icon="X", difficulty="beginner"
        )
        assert lp.order == 0

    def test_ordering(self, learning_path, other_path):
        paths = list(LearningPath.objects.all())
        assert paths[0].order < paths[1].order

    def test_difficulty_beginner(self, learning_path):
        assert learning_path.difficulty == "beginner"

    def test_difficulty_intermediate(self, other_path):
        assert other_path.difficulty == "intermediate"

    def test_difficulty_advanced(self, db):
        lp = LearningPath.objects.create(
            slug="adv", title="Adv", description="D", icon="X", difficulty="advanced"
        )
        assert lp.difficulty == "advanced"

    def test_icon_stores_emoji(self, learning_path):
        assert learning_path.icon == "\U0001F9E0"

    def test_update_title(self, learning_path):
        learning_path.title = "Updated"
        learning_path.save()
        learning_path.refresh_from_db()
        assert learning_path.title == "Updated"

    def test_description_can_be_long(self, db):
        lp = LearningPath.objects.create(
            slug="long", title="Long", description="A" * 5000, icon="X", difficulty="beginner"
        )
        lp.refresh_from_db()
        assert len(lp.description) == 5000

    def test_lessons_related_name(self, learning_path, lesson):
        assert lesson in learning_path.lessons.all()

    def test_cascade_deletes_lessons(self, learning_path, lesson):
        learning_path.delete()
        assert Lesson.objects.count() == 0


# ── Lesson Model ─────────────────────────────────────────────


class TestLesson:
    def test_create(self, lesson):
        assert lesson.pk is not None

    def test_str_returns_title(self, lesson):
        assert str(lesson) == "Intro to AI"

    def test_slug_unique(self, lesson, learning_path):
        with pytest.raises(IntegrityError):
            Lesson.objects.create(path=learning_path, slug="intro-ai", title="Dup")

    def test_default_xp_reward(self, learning_path):
        l = Lesson.objects.create(path=learning_path, slug="default-xp", title="T")
        assert l.xp_reward == 10

    def test_default_order(self, learning_path):
        l = Lesson.objects.create(path=learning_path, slug="default-ord", title="T")
        assert l.order == 0

    def test_description_blank_allowed(self, learning_path):
        l = Lesson.objects.create(path=learning_path, slug="blank-desc", title="T")
        assert l.description == ""

    def test_content_blank_allowed(self, learning_path):
        l = Lesson.objects.create(path=learning_path, slug="blank-content", title="T")
        assert l.content == ""

    def test_ai_system_prompt_blank_allowed(self, learning_path):
        l = Lesson.objects.create(path=learning_path, slug="blank-prompt", title="T")
        assert l.ai_system_prompt == ""

    def test_ordering(self, lesson, other_lesson):
        lessons = list(Lesson.objects.all())
        assert lessons[0].order < lessons[1].order

    def test_fk_to_learning_path(self, lesson, learning_path):
        assert lesson.path == learning_path

    def test_content_stores_markdown(self, lesson):
        assert lesson.content == "# Welcome"

    def test_ai_system_prompt_stores_text(self, lesson):
        assert lesson.ai_system_prompt == "You are a helpful tutor."

    def test_update_xp_reward(self, lesson):
        lesson.xp_reward = 50
        lesson.save()
        lesson.refresh_from_db()
        assert lesson.xp_reward == 50

    def test_cascade_delete_path(self, lesson, learning_path):
        lesson_id = lesson.id
        learning_path.delete()
        assert not Lesson.objects.filter(id=lesson_id).exists()


# ── LessonProgress Model ────────────────────────────────────


class TestLessonProgress:
    def test_create(self, user, lesson):
        lp = LessonProgress.objects.create(user=user, lesson=lesson)
        assert lp.pk is not None

    def test_str_format(self, user, lesson):
        lp = LessonProgress.objects.create(user=user, lesson=lesson)
        assert str(lp) == "testuser - Intro to AI"

    def test_default_completed_false(self, user, lesson):
        lp = LessonProgress.objects.create(user=user, lesson=lesson)
        assert lp.completed is False

    def test_default_completed_at_none(self, user, lesson):
        lp = LessonProgress.objects.create(user=user, lesson=lesson)
        assert lp.completed_at is None

    def test_mark_completed(self, user, lesson):
        lp = LessonProgress.objects.create(user=user, lesson=lesson)
        lp.completed = True
        lp.completed_at = timezone.now()
        lp.save()
        lp.refresh_from_db()
        assert lp.completed is True
        assert lp.completed_at is not None

    def test_unique_together(self, user, lesson):
        LessonProgress.objects.create(user=user, lesson=lesson)
        with pytest.raises(IntegrityError):
            LessonProgress.objects.create(user=user, lesson=lesson)

    def test_different_users_same_lesson(self, user, other_user, lesson):
        LessonProgress.objects.create(user=user, lesson=lesson)
        lp2 = LessonProgress.objects.create(user=other_user, lesson=lesson)
        assert lp2.pk is not None

    def test_same_user_different_lessons(self, user, lesson, other_lesson):
        LessonProgress.objects.create(user=user, lesson=lesson)
        lp2 = LessonProgress.objects.create(user=user, lesson=other_lesson)
        assert lp2.pk is not None

    def test_cascade_delete_user(self, user, lesson):
        LessonProgress.objects.create(user=user, lesson=lesson)
        user.delete()
        assert LessonProgress.objects.count() == 0

    def test_cascade_delete_lesson(self, user, lesson):
        LessonProgress.objects.create(user=user, lesson=lesson)
        lesson.delete()
        assert LessonProgress.objects.count() == 0

    def test_related_name_from_user(self, user, lesson):
        lp = LessonProgress.objects.create(user=user, lesson=lesson)
        assert lp in user.lesson_progress.all()

    def test_related_name_from_lesson(self, user, lesson):
        lp = LessonProgress.objects.create(user=user, lesson=lesson)
        assert lp in lesson.progress.all()


# ── LearningPath List API ───────────────────────────────────


class TestLearningPathListAPI:
    def test_list_paths_authenticated(self, auth_client, learning_path):
        resp = auth_client.get("/api/v1/paths/")
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_list_paths_unauthenticated(self, client, learning_path):
        resp = client.get("/api/v1/paths/")
        assert resp.status_code in (401, 403)

    def test_list_paths_contains_progress_fields(self, auth_client, learning_path):
        resp = auth_client.get("/api/v1/paths/")
        entry = resp.data[0]
        assert "lessons_count" in entry
        assert "completed_count" in entry
        assert "progress_percent" in entry

    def test_list_paths_lessons_count(self, auth_client, learning_path, lesson, other_lesson):
        resp = auth_client.get("/api/v1/paths/")
        assert resp.data[0]["lessons_count"] == 2

    def test_list_paths_no_progress(self, auth_client, learning_path, lesson):
        resp = auth_client.get("/api/v1/paths/")
        assert resp.data[0]["completed_count"] == 0
        assert resp.data[0]["progress_percent"] == 0

    def test_list_paths_with_progress(self, auth_client, user, learning_path, lesson, other_lesson):
        LessonProgress.objects.create(user=user, lesson=lesson, completed=True)
        resp = auth_client.get("/api/v1/paths/")
        assert resp.data[0]["completed_count"] == 1
        assert resp.data[0]["progress_percent"] == 50

    def test_list_paths_full_progress(self, auth_client, user, learning_path, lesson, other_lesson):
        LessonProgress.objects.create(user=user, lesson=lesson, completed=True)
        LessonProgress.objects.create(user=user, lesson=other_lesson, completed=True)
        resp = auth_client.get("/api/v1/paths/")
        assert resp.data[0]["progress_percent"] == 100

    def test_list_paths_ordering(self, auth_client, learning_path, other_path):
        resp = auth_client.get("/api/v1/paths/")
        assert resp.data[0]["order"] <= resp.data[1]["order"]

    def test_list_paths_empty(self, auth_client):
        resp = auth_client.get("/api/v1/paths/")
        assert resp.status_code == 200
        assert resp.data == []


# ── LearningPath Detail API ─────────────────────────────────


class TestLearningPathDetailAPI:
    def test_get_path_by_slug(self, auth_client, learning_path, lesson):
        resp = auth_client.get(f"/api/v1/paths/{learning_path.slug}/")
        assert resp.status_code == 200
        assert resp.data["title"] == "AI Grundlagen"

    def test_path_detail_includes_lessons(self, auth_client, learning_path, lesson, other_lesson):
        resp = auth_client.get(f"/api/v1/paths/{learning_path.slug}/")
        assert len(resp.data["lessons"]) == 2

    def test_path_detail_lessons_ordered(self, auth_client, learning_path, lesson, other_lesson):
        resp = auth_client.get(f"/api/v1/paths/{learning_path.slug}/")
        orders = [l["order"] for l in resp.data["lessons"]]
        assert orders == sorted(orders)

    def test_path_detail_unauthenticated(self, client, learning_path):
        resp = client.get(f"/api/v1/paths/{learning_path.slug}/")
        assert resp.status_code in (401, 403)

    def test_path_detail_not_found(self, auth_client):
        resp = auth_client.get("/api/v1/paths/nonexistent/")
        assert resp.status_code == 404


# ── Lesson Detail API ───────────────────────────────────────


class TestLessonDetailAPI:
    def test_get_lesson_by_slug(self, auth_client, lesson):
        resp = auth_client.get(f"/api/v1/lessons/{lesson.slug}/")
        assert resp.status_code == 200
        assert resp.data["title"] == "Intro to AI"

    def test_lesson_detail_contains_content(self, auth_client, lesson):
        resp = auth_client.get(f"/api/v1/lessons/{lesson.slug}/")
        assert resp.data["content"] == "# Welcome"

    def test_lesson_detail_contains_system_prompt(self, auth_client, lesson):
        resp = auth_client.get(f"/api/v1/lessons/{lesson.slug}/")
        assert resp.data["ai_system_prompt"] == "You are a helpful tutor."

    def test_lesson_detail_unauthenticated(self, client, lesson):
        resp = client.get(f"/api/v1/lessons/{lesson.slug}/")
        assert resp.status_code in (401, 403)

    def test_lesson_detail_not_found(self, auth_client):
        resp = auth_client.get("/api/v1/lessons/nonexistent/")
        assert resp.status_code == 404

    def test_lesson_detail_all_fields(self, auth_client, lesson):
        resp = auth_client.get(f"/api/v1/lessons/{lesson.slug}/")
        for field in ("id", "slug", "title", "description", "content", "xp_reward", "order", "ai_system_prompt"):
            assert field in resp.data


# ── Lesson Complete API ──────────────────────────────────────


class TestLessonCompleteAPI:
    def test_complete_lesson_success(self, auth_client, lesson):
        resp = auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        assert resp.status_code == 200
        assert resp.data["already_completed"] is False

    def test_complete_lesson_awards_xp(self, auth_client, user, lesson):
        auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        user.profile.refresh_from_db()
        assert user.profile.xp == lesson.xp_reward

    def test_complete_lesson_updates_level(self, auth_client, user, lesson):
        user.profile.xp = 95
        user.profile.save()
        auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        user.profile.refresh_from_db()
        assert user.profile.xp == 105
        assert user.profile.level == 2

    def test_complete_lesson_creates_progress(self, auth_client, user, lesson):
        auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        progress = LessonProgress.objects.get(user=user, lesson=lesson)
        assert progress.completed is True
        assert progress.completed_at is not None

    def test_complete_lesson_double_no_extra_xp(self, auth_client, user, lesson):
        auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        user.profile.refresh_from_db()
        assert user.profile.xp == lesson.xp_reward

    def test_complete_lesson_double_returns_already_completed(self, auth_client, lesson):
        auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        resp = auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        assert resp.data["already_completed"] is True

    def test_complete_lesson_returns_profile(self, auth_client, lesson):
        resp = auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        assert "profile" in resp.data
        assert resp.data["profile"]["xp"] == lesson.xp_reward

    def test_complete_lesson_unlocks_achievement(self, auth_client, user, lesson, db):
        Achievement.objects.create(
            slug="first",
            name="First",
            description="D",
            icon="X",
            requirement_type="lessons_completed",
            requirement_value=1,
            xp_reward=20,
        )
        resp = auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        assert len(resp.data["new_achievements"]) == 1
        assert resp.data["new_achievements"][0]["achievement"]["slug"] == "first"

    def test_complete_lesson_xp_achievement(self, auth_client, user, lesson, db):
        user.profile.xp = 95
        user.profile.save()
        Achievement.objects.create(
            slug="xp100",
            name="Century",
            description="D",
            icon="X",
            requirement_type="xp_total",
            requirement_value=100,
        )
        resp = auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        assert len(resp.data["new_achievements"]) == 1

    def test_complete_lesson_no_duplicate_achievement(self, auth_client, user, lesson, other_lesson, db):
        ach = Achievement.objects.create(
            slug="first",
            name="First",
            description="D",
            icon="X",
            requirement_type="lessons_completed",
            requirement_value=1,
        )
        auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        resp = auth_client.post(f"/api/v1/lessons/{other_lesson.slug}/complete/")
        assert len(resp.data["new_achievements"]) == 0
        assert UserAchievement.objects.filter(user=user, achievement=ach).count() == 1

    def test_complete_lesson_not_found(self, auth_client):
        resp = auth_client.post("/api/v1/lessons/nonexistent/complete/")
        assert resp.status_code == 404

    def test_complete_lesson_unauthenticated(self, client, lesson):
        resp = client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        assert resp.status_code in (401, 403)

    def test_complete_multiple_lessons_cumulative_xp(self, auth_client, user, lesson, other_lesson):
        auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        auth_client.post(f"/api/v1/lessons/{other_lesson.slug}/complete/")
        user.profile.refresh_from_db()
        assert user.profile.xp == lesson.xp_reward + other_lesson.xp_reward

    def test_complete_lesson_level_calculation(self, auth_client, user, lesson):
        user.profile.xp = 290
        user.profile.save()
        auth_client.post(f"/api/v1/lessons/{lesson.slug}/complete/")
        user.profile.refresh_from_db()
        # 290 + 10 = 300 → level = 300 // 100 + 1 = 4
        assert user.profile.level == 4
