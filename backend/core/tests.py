import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.test import APIClient

from core.models import Achievement, UserAchievement, UserProfile
from lessons.models import LearningPath, Lesson, LessonProgress


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="otheruser", password="testpass123")


@pytest.fixture
def achievement(db):
    return Achievement.objects.create(
        slug="first-lesson",
        name="First Lesson",
        description="Complete your first lesson",
        icon="\U0001F3C6",
        xp_reward=50,
        requirement_type="lessons_completed",
        requirement_value=1,
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


# ── UserProfile Model ───────────────────────────────────────


class TestUserProfile:
    def test_auto_created_on_user_creation(self, user):
        assert hasattr(user, "profile")
        assert isinstance(user.profile, UserProfile)

    def test_default_xp(self, user):
        assert user.profile.xp == 0

    def test_default_level(self, user):
        assert user.profile.level == 1

    def test_default_streak_days(self, user):
        assert user.profile.streak_days == 0

    def test_default_avatar_color(self, user):
        assert user.profile.avatar_color == "#00A76F"

    def test_last_activity_auto_set(self, user):
        assert user.profile.last_activity is not None

    def test_str_returns_username(self, user):
        assert str(user.profile) == "testuser"

    def test_update_xp(self, user):
        user.profile.xp = 100
        user.profile.save()
        user.profile.refresh_from_db()
        assert user.profile.xp == 100

    def test_update_level(self, user):
        user.profile.level = 5
        user.profile.save()
        user.profile.refresh_from_db()
        assert user.profile.level == 5

    def test_update_streak_days(self, user):
        user.profile.streak_days = 7
        user.profile.save()
        user.profile.refresh_from_db()
        assert user.profile.streak_days == 7

    def test_update_avatar_color(self, user):
        user.profile.avatar_color = "#FF5630"
        user.profile.save()
        user.profile.refresh_from_db()
        assert user.profile.avatar_color == "#FF5630"

    def test_one_to_one_constraint(self, user):
        with pytest.raises(IntegrityError):
            UserProfile.objects.create(user=user)

    def test_cascade_delete(self, user):
        profile_id = user.profile.id
        user.delete()
        assert not UserProfile.objects.filter(id=profile_id).exists()

    def test_related_name_from_user(self, user):
        assert user.profile == UserProfile.objects.get(user=user)

    def test_negative_xp_allowed(self, user):
        user.profile.xp = -10
        user.profile.save()
        user.profile.refresh_from_db()
        assert user.profile.xp == -10

    def test_avatar_color_max_length(self, user):
        user.profile.avatar_color = "#FFFFFF"
        user.profile.save()
        user.profile.refresh_from_db()
        assert user.profile.avatar_color == "#FFFFFF"


# ── Achievement Model ────────────────────────────────────────


class TestAchievement:
    def test_create(self, achievement):
        assert achievement.pk is not None

    def test_str_returns_name(self, achievement):
        assert str(achievement) == "First Lesson"

    def test_slug_unique(self, db, achievement):
        with pytest.raises(IntegrityError):
            Achievement.objects.create(
                slug="first-lesson",
                name="Duplicate",
                description="Dup",
                icon="X",
                requirement_type="streak",
            )

    def test_default_xp_reward(self, db):
        a = Achievement.objects.create(
            slug="test-default",
            name="Test",
            description="D",
            icon="X",
            requirement_type="streak",
        )
        assert a.xp_reward == 0

    def test_default_requirement_value(self, db):
        a = Achievement.objects.create(
            slug="test-req",
            name="Test",
            description="D",
            icon="X",
            requirement_type="xp_total",
        )
        assert a.requirement_value == 1

    def test_requirement_type_choices(self, achievement):
        valid = {"lessons_completed", "streak", "xp_total", "first_chat"}
        assert achievement.requirement_type in valid

    def test_icon_stores_emoji(self, achievement):
        assert achievement.icon == "\U0001F3C6"

    def test_update_name(self, achievement):
        achievement.name = "Updated"
        achievement.save()
        achievement.refresh_from_db()
        assert achievement.name == "Updated"

    def test_description_can_be_long(self, db):
        long_desc = "A" * 5000
        a = Achievement.objects.create(
            slug="long-desc",
            name="Long",
            description=long_desc,
            icon="X",
            requirement_type="streak",
        )
        a.refresh_from_db()
        assert len(a.description) == 5000

    def test_xp_reward_large_value(self, db):
        a = Achievement.objects.create(
            slug="big-xp",
            name="Big XP",
            description="D",
            icon="X",
            xp_reward=999999,
            requirement_type="xp_total",
        )
        assert a.xp_reward == 999999

    def test_xp_reward_zero(self, achievement):
        achievement.xp_reward = 0
        achievement.save()
        achievement.refresh_from_db()
        assert achievement.xp_reward == 0


# ── UserAchievement Model ───────────────────────────────────


class TestUserAchievement:
    def test_create(self, user, achievement):
        ua = UserAchievement.objects.create(user=user, achievement=achievement)
        assert ua.pk is not None

    def test_str_format(self, user, achievement):
        ua = UserAchievement.objects.create(user=user, achievement=achievement)
        assert str(ua) == "testuser - First Lesson"

    def test_unlocked_at_auto_set(self, user, achievement):
        ua = UserAchievement.objects.create(user=user, achievement=achievement)
        assert ua.unlocked_at is not None

    def test_unique_together(self, user, achievement):
        UserAchievement.objects.create(user=user, achievement=achievement)
        with pytest.raises(IntegrityError):
            UserAchievement.objects.create(user=user, achievement=achievement)

    def test_different_users_same_achievement(self, user, other_user, achievement):
        UserAchievement.objects.create(user=user, achievement=achievement)
        ua2 = UserAchievement.objects.create(user=other_user, achievement=achievement)
        assert ua2.pk is not None

    def test_cascade_delete_user(self, user, achievement):
        UserAchievement.objects.create(user=user, achievement=achievement)
        user.delete()
        assert UserAchievement.objects.count() == 0

    def test_cascade_delete_achievement(self, user, achievement):
        UserAchievement.objects.create(user=user, achievement=achievement)
        achievement.delete()
        assert UserAchievement.objects.count() == 0

    def test_related_name_from_user(self, user, achievement):
        ua = UserAchievement.objects.create(user=user, achievement=achievement)
        assert ua in user.user_achievements.all()

    def test_multiple_achievements_per_user(self, user, achievement, db):
        a2 = Achievement.objects.create(
            slug="second",
            name="Second",
            description="D",
            icon="X",
            requirement_type="streak",
        )
        UserAchievement.objects.create(user=user, achievement=achievement)
        UserAchievement.objects.create(user=user, achievement=a2)
        assert user.user_achievements.count() == 2

    def test_user_fk_is_required(self, achievement):
        with pytest.raises(IntegrityError):
            UserAchievement.objects.create(user=None, achievement=achievement)

    def test_achievement_fk_is_required(self, user):
        with pytest.raises(IntegrityError):
            UserAchievement.objects.create(user=user, achievement=None)


# ── Profile API ──────────────────────────────────────────────


class TestProfileAPI:
    def test_get_profile_authenticated(self, auth_client, user):
        resp = auth_client.get("/api/v1/profile/")
        assert resp.status_code == 200
        assert resp.data["user"]["username"] == "testuser"
        assert resp.data["xp"] == 0
        assert resp.data["level"] == 1

    def test_get_profile_unauthenticated(self, client):
        resp = client.get("/api/v1/profile/")
        assert resp.status_code in (401, 403)

    def test_profile_contains_all_fields(self, auth_client):
        resp = auth_client.get("/api/v1/profile/")
        for field in ("id", "user", "xp", "level", "streak_days", "last_activity", "avatar_color"):
            assert field in resp.data

    def test_profile_user_nested(self, auth_client):
        resp = auth_client.get("/api/v1/profile/")
        assert "id" in resp.data["user"]
        assert "username" in resp.data["user"]

    def test_profile_reflects_xp_changes(self, auth_client, user):
        user.profile.xp = 250
        user.profile.save()
        resp = auth_client.get("/api/v1/profile/")
        assert resp.data["xp"] == 250


# ── Leaderboard API ─────────────────────────────────────────


class TestLeaderboardAPI:
    def test_leaderboard_no_auth_required(self, client, user):
        resp = client.get("/api/v1/leaderboard/")
        assert resp.status_code == 200

    def test_leaderboard_returns_list(self, client, user):
        resp = client.get("/api/v1/leaderboard/")
        assert isinstance(resp.data, list)

    def test_leaderboard_ordered_by_xp_desc(self, client, user, other_user):
        user.profile.xp = 100
        user.profile.save()
        other_user.profile.xp = 200
        other_user.profile.save()
        resp = client.get("/api/v1/leaderboard/")
        assert resp.data[0]["xp"] >= resp.data[1]["xp"]

    def test_leaderboard_contains_fields(self, client, user):
        resp = client.get("/api/v1/leaderboard/")
        entry = resp.data[0]
        for field in ("id", "username", "xp", "level", "avatar_color"):
            assert field in entry

    def test_leaderboard_max_20(self, client, db):
        for i in range(25):
            User.objects.create_user(username=f"user{i}", password="pass")
        resp = client.get("/api/v1/leaderboard/")
        assert len(resp.data) <= 20

    def test_leaderboard_empty_db(self, client, db):
        resp = client.get("/api/v1/leaderboard/")
        assert resp.status_code == 200
        assert resp.data == []


# ── Achievements API ─────────────────────────────────────────


class TestAchievementsAPI:
    def test_list_achievements_authenticated(self, auth_client, achievement):
        resp = auth_client.get("/api/v1/achievements/")
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_list_achievements_unauthenticated(self, client, achievement):
        resp = client.get("/api/v1/achievements/")
        assert resp.status_code in (401, 403)

    def test_achievement_contains_unlock_info(self, auth_client, achievement):
        resp = auth_client.get("/api/v1/achievements/")
        entry = resp.data[0]
        assert "unlocked" in entry
        assert "unlocked_at" in entry

    def test_achievement_not_unlocked(self, auth_client, achievement):
        resp = auth_client.get("/api/v1/achievements/")
        assert resp.data[0]["unlocked"] is False
        assert resp.data[0]["unlocked_at"] is None

    def test_achievement_unlocked(self, auth_client, user, achievement):
        UserAchievement.objects.create(user=user, achievement=achievement)
        resp = auth_client.get("/api/v1/achievements/")
        assert resp.data[0]["unlocked"] is True
        assert resp.data[0]["unlocked_at"] is not None

    def test_achievements_empty(self, auth_client):
        resp = auth_client.get("/api/v1/achievements/")
        assert resp.status_code == 200
        assert resp.data == []


# ── Login API ────────────────────────────────────────────────


class TestLoginAPI:
    def test_login_success(self, client, user):
        resp = client.post(
            "/api/v1/auth/login/",
            {"username": "testuser", "password": "testpass123"},
        )
        assert resp.status_code == 200
        assert resp.data["username"] == "testuser"

    def test_login_wrong_password(self, client, user):
        resp = client.post(
            "/api/v1/auth/login/",
            {"username": "testuser", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_login_missing_username(self, client):
        resp = client.post("/api/v1/auth/login/", {"password": "testpass123"})
        assert resp.status_code == 400

    def test_login_missing_password(self, client):
        resp = client.post("/api/v1/auth/login/", {"username": "testuser"})
        assert resp.status_code == 400

    def test_login_nonexistent_user(self, client, db):
        resp = client.post(
            "/api/v1/auth/login/",
            {"username": "ghost", "password": "pass"},
        )
        assert resp.status_code == 401

    def test_login_empty_body(self, client, db):
        resp = client.post("/api/v1/auth/login/", {})
        assert resp.status_code == 400

    def test_login_returns_user_id(self, client, user):
        resp = client.post(
            "/api/v1/auth/login/",
            {"username": "testuser", "password": "testpass123"},
        )
        assert resp.data["id"] == user.id


# ── Demo Users API ──────────────────────────────────────────


@pytest.fixture
def demo_users(db):
    users = []
    for data in [
        ("demo", "Gina", "M.", "#00A76F"),
        ("anna", "Anna", "M.", "#8E33FF"),
        ("marco", "Marco", "L.", "#00B8D9"),
    ]:
        u = User.objects.create_user(
            username=data[0],
            password=f"{data[0]}1234",
            first_name=data[1],
            last_name=data[2],
        )
        u.profile.avatar_color = data[3]
        u.profile.save()
        users.append(u)
    return users


class TestDemoUsersAPI:
    def test_returns_200(self, client, demo_users):
        resp = client.get("/api/v1/auth/demo-users/")
        assert resp.status_code == 200

    def test_no_auth_required(self, client, demo_users):
        resp = client.get("/api/v1/auth/demo-users/")
        assert resp.status_code == 200

    def test_returns_all_demo_users(self, client, demo_users):
        resp = client.get("/api/v1/auth/demo-users/")
        assert len(resp.data) == 3

    def test_contains_required_fields(self, client, demo_users):
        resp = client.get("/api/v1/auth/demo-users/")
        for entry in resp.data:
            assert "username" in entry
            assert "display_name" in entry
            assert "avatar_color" in entry
            assert "role" in entry

    def test_does_not_contain_password(self, client, demo_users):
        resp = client.get("/api/v1/auth/demo-users/")
        for entry in resp.data:
            assert "password" not in entry

    def test_display_name_format(self, client, demo_users):
        resp = client.get("/api/v1/auth/demo-users/")
        names = {e["username"]: e["display_name"] for e in resp.data}
        assert names["demo"] == "Gina M."
        assert names["anna"] == "Anna M."

    def test_roles_assigned(self, client, demo_users):
        resp = client.get("/api/v1/auth/demo-users/")
        roles = {e["username"]: e["role"] for e in resp.data}
        assert roles["demo"] == "Lernende"
        assert roles["anna"] == "Top-Lernende"
        assert roles["marco"] == "Fortgeschritten"

    def test_avatar_colors(self, client, demo_users):
        resp = client.get("/api/v1/auth/demo-users/")
        colors = {e["username"]: e["avatar_color"] for e in resp.data}
        assert colors["demo"] == "#00A76F"
        assert colors["anna"] == "#8E33FF"

    def test_empty_when_no_demo_users(self, client, db):
        resp = client.get("/api/v1/auth/demo-users/")
        assert resp.status_code == 200
        assert resp.data == []

    def test_ignores_non_demo_users(self, client, user, demo_users):
        resp = client.get("/api/v1/auth/demo-users/")
        usernames = [e["username"] for e in resp.data]
        assert "testuser" not in usernames


# ── Leaderboard display_name & streak_days ──────────────────


class TestLeaderboardDisplayName:
    def test_display_name_field_present(self, client, user):
        resp = client.get("/api/v1/leaderboard/")
        assert "display_name" in resp.data[0]

    def test_streak_days_field_present(self, client, user):
        resp = client.get("/api/v1/leaderboard/")
        assert "streak_days" in resp.data[0]

    def test_display_name_from_first_last(self, client, db):
        u = User.objects.create_user(
            username="jane", password="pass", first_name="Jane", last_name="Doe"
        )
        resp = client.get("/api/v1/leaderboard/")
        entry = next(e for e in resp.data if e["username"] == "jane")
        assert entry["display_name"] == "Jane Doe"

    def test_display_name_fallback_to_username(self, client, user):
        """User without first/last name falls back to username."""
        resp = client.get("/api/v1/leaderboard/")
        entry = next(e for e in resp.data if e["username"] == "testuser")
        assert entry["display_name"] == "testuser"

    def test_display_name_first_name_only(self, client, db):
        User.objects.create_user(username="first_only", password="pass", first_name="Alice")
        resp = client.get("/api/v1/leaderboard/")
        entry = next(e for e in resp.data if e["username"] == "first_only")
        assert entry["display_name"] == "Alice"

    def test_display_name_last_name_only(self, client, db):
        User.objects.create_user(username="last_only", password="pass", last_name="Smith")
        resp = client.get("/api/v1/leaderboard/")
        entry = next(e for e in resp.data if e["username"] == "last_only")
        assert entry["display_name"] == "Smith"

    def test_streak_days_zero_default(self, client, user):
        resp = client.get("/api/v1/leaderboard/")
        entry = next(e for e in resp.data if e["username"] == "testuser")
        assert entry["streak_days"] == 0

    def test_streak_days_reflects_profile(self, client, user):
        user.profile.streak_days = 7
        user.profile.save()
        resp = client.get("/api/v1/leaderboard/")
        entry = next(e for e in resp.data if e["username"] == "testuser")
        assert entry["streak_days"] == 7

    def test_streak_days_large_value(self, client, user):
        user.profile.streak_days = 365
        user.profile.save()
        resp = client.get("/api/v1/leaderboard/")
        entry = next(e for e in resp.data if e["username"] == "testuser")
        assert entry["streak_days"] == 365

    def test_display_name_with_spaces(self, client, db):
        User.objects.create_user(
            username="spacey", password="pass",
            first_name="  ", last_name="  ",
        )
        resp = client.get("/api/v1/leaderboard/")
        entry = next(e for e in resp.data if e["username"] == "spacey")
        # strip() removes whitespace, falls back to username
        assert entry["display_name"] == "spacey"

    def test_display_name_special_chars(self, client, db):
        User.objects.create_user(
            username="special", password="pass",
            first_name="Hans-Peter", last_name="Müller",
        )
        resp = client.get("/api/v1/leaderboard/")
        entry = next(e for e in resp.data if e["username"] == "special")
        assert entry["display_name"] == "Hans-Peter Müller"

    def test_multiple_users_display_names(self, client, demo_users):
        resp = client.get("/api/v1/leaderboard/")
        names = {e["username"]: e["display_name"] for e in resp.data}
        assert names["demo"] == "Gina M."
        assert names["anna"] == "Anna M."
        assert names["marco"] == "Marco L."

    def test_leaderboard_still_ordered_by_xp(self, client, db):
        u1 = User.objects.create_user(username="u1", password="pass", first_name="A", last_name="B")
        u2 = User.objects.create_user(username="u2", password="pass", first_name="C", last_name="D")
        u1.profile.xp = 50
        u1.profile.save()
        u2.profile.xp = 200
        u2.profile.save()
        resp = client.get("/api/v1/leaderboard/")
        assert resp.data[0]["username"] == "u2"
        assert resp.data[1]["username"] == "u1"

    def test_all_expected_fields(self, client, user):
        resp = client.get("/api/v1/leaderboard/")
        entry = resp.data[0]
        expected = {"id", "username", "display_name", "xp", "level", "streak_days", "avatar_color"}
        assert expected == set(entry.keys())


# ── Achievement Progress ──────────────────────────────────────


@pytest.fixture
def achievement_streak(db):
    return Achievement.objects.create(
        slug="three-streak",
        name="On Fire",
        description="3-day streak",
        icon="\U0001F525",
        xp_reward=30,
        requirement_type="streak",
        requirement_value=3,
    )


@pytest.fixture
def achievement_xp(db):
    return Achievement.objects.create(
        slug="xp-100",
        name="Century",
        description="Earn 100 XP",
        icon="\u26A1",
        xp_reward=25,
        requirement_type="xp_total",
        requirement_value=100,
    )


@pytest.fixture
def achievement_chat(db):
    return Achievement.objects.create(
        slug="first-chat",
        name="Chatter",
        description="Send first chat",
        icon="\U0001F4AC",
        xp_reward=15,
        requirement_type="first_chat",
        requirement_value=1,
    )


@pytest.fixture
def lesson_for_progress(db):
    path = LearningPath.objects.create(
        slug="test-path", title="Test", description="D", icon="X", difficulty="beginner"
    )
    return Lesson.objects.create(path=path, slug="lesson-1", title="L1", xp_reward=10, order=1)


@pytest.fixture
def second_lesson_for_progress(db):
    path = LearningPath.objects.get(slug="test-path")
    return Lesson.objects.create(path=path, slug="lesson-2", title="L2", xp_reward=10, order=2)


class TestAchievementProgress:
    def test_progress_field_present(self, auth_client, achievement):
        resp = auth_client.get("/api/v1/achievements/")
        assert "progress" in resp.data[0]

    def test_progress_has_current_and_target(self, auth_client, achievement):
        resp = auth_client.get("/api/v1/achievements/")
        progress = resp.data[0]["progress"]
        assert "current" in progress
        assert "target" in progress

    def test_progress_target_matches_requirement(self, auth_client, achievement):
        resp = auth_client.get("/api/v1/achievements/")
        assert resp.data[0]["progress"]["target"] == achievement.requirement_value

    def test_lessons_completed_progress_zero(self, auth_client, achievement):
        """No lessons completed → current = 0."""
        resp = auth_client.get("/api/v1/achievements/")
        assert resp.data[0]["progress"]["current"] == 0

    def test_lessons_completed_progress_partial(self, auth_client, user, achievement, lesson_for_progress):
        """Achievement requires 1 lesson, user completed 1 → current = 1."""
        LessonProgress.objects.create(user=user, lesson=lesson_for_progress, completed=True)
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "first-lesson")
        assert entry["progress"]["current"] == 1
        assert entry["progress"]["target"] == 1

    def test_lessons_completed_progress_capped_at_target(
        self, auth_client, user, achievement, lesson_for_progress, second_lesson_for_progress
    ):
        """Current capped at target — never exceeds it."""
        LessonProgress.objects.create(user=user, lesson=lesson_for_progress, completed=True)
        LessonProgress.objects.create(user=user, lesson=second_lesson_for_progress, completed=True)
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "first-lesson")
        # requirement_value is 1, user has 2 completed → capped at 1
        assert entry["progress"]["current"] == 1

    def test_streak_progress_zero(self, auth_client, user, achievement_streak):
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "three-streak")
        assert entry["progress"]["current"] == 0
        assert entry["progress"]["target"] == 3

    def test_streak_progress_partial(self, auth_client, user, achievement_streak):
        user.profile.streak_days = 2
        user.profile.save()
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "three-streak")
        assert entry["progress"]["current"] == 2

    def test_streak_progress_met(self, auth_client, user, achievement_streak):
        user.profile.streak_days = 3
        user.profile.save()
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "three-streak")
        assert entry["progress"]["current"] == 3

    def test_streak_progress_capped(self, auth_client, user, achievement_streak):
        user.profile.streak_days = 10
        user.profile.save()
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "three-streak")
        assert entry["progress"]["current"] == 3  # capped at target

    def test_xp_progress_zero(self, auth_client, user, achievement_xp):
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "xp-100")
        assert entry["progress"]["current"] == 0
        assert entry["progress"]["target"] == 100

    def test_xp_progress_partial(self, auth_client, user, achievement_xp):
        user.profile.xp = 42
        user.profile.save()
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "xp-100")
        assert entry["progress"]["current"] == 42

    def test_xp_progress_met(self, auth_client, user, achievement_xp):
        user.profile.xp = 100
        user.profile.save()
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "xp-100")
        assert entry["progress"]["current"] == 100

    def test_xp_progress_capped(self, auth_client, user, achievement_xp):
        user.profile.xp = 999
        user.profile.save()
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "xp-100")
        assert entry["progress"]["current"] == 100

    def test_first_chat_progress_zero(self, auth_client, user, achievement_chat):
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "first-chat")
        assert entry["progress"]["current"] == 0
        assert entry["progress"]["target"] == 1

    def test_first_chat_progress_met(self, auth_client, user, achievement_chat, db):
        from chat.models import ChatMessage

        ChatMessage.objects.create(user=user, role="user", content="Hello")
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "first-chat")
        assert entry["progress"]["current"] == 1

    def test_progress_still_shown_when_unlocked(self, auth_client, user, achievement, lesson_for_progress):
        """Even after unlocking, progress field should be present."""
        LessonProgress.objects.create(user=user, lesson=lesson_for_progress, completed=True)
        UserAchievement.objects.create(user=user, achievement=achievement)
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "first-lesson")
        assert entry["unlocked"] is True
        assert entry["progress"]["current"] == 1

    def test_multiple_achievements_each_has_progress(
        self, auth_client, user, achievement, achievement_streak, achievement_xp
    ):
        resp = auth_client.get("/api/v1/achievements/")
        assert len(resp.data) == 3
        for entry in resp.data:
            assert "progress" in entry
            assert "current" in entry["progress"]
            assert "target" in entry["progress"]

    def test_incomplete_lessons_not_counted(self, auth_client, user, achievement, lesson_for_progress):
        """LessonProgress with completed=False should not count."""
        LessonProgress.objects.create(user=user, lesson=lesson_for_progress, completed=False)
        resp = auth_client.get("/api/v1/achievements/")
        entry = next(a for a in resp.data if a["slug"] == "first-lesson")
        assert entry["progress"]["current"] == 0


# ── Analytics API ────────────────────────────────────────────


@pytest.fixture
def analytics_path(db):
    return LearningPath.objects.create(
        slug="analytics-path", title="Analytics Path", description="D",
        icon="\U0001F9E0", difficulty="beginner", order=1,
    )


@pytest.fixture
def analytics_lesson(analytics_path):
    return Lesson.objects.create(
        path=analytics_path, slug="a-lesson-1", title="A Lesson 1",
        content="Content", xp_reward=10, order=1,
    )


@pytest.fixture
def analytics_lesson_2(analytics_path):
    return Lesson.objects.create(
        path=analytics_path, slug="a-lesson-2", title="A Lesson 2",
        content="Content", xp_reward=15, order=2,
    )


class TestAnalyticsEndpoint:
    def test_requires_auth(self, client, db):
        resp = client.get("/api/v1/analytics/")
        assert resp.status_code in (401, 403)

    def test_returns_200(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.status_code == 200

    def test_contains_all_sections(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        expected = {
            "overview", "xp_distribution", "popular_lessons",
            "path_progress", "activity_last_7_days",
            "achievements_summary", "chat_stats",
        }
        assert expected == set(resp.data.keys())


class TestAnalyticsOverview:
    def test_overview_fields(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        ov = resp.data["overview"]
        expected = {
            "total_users", "active_users_today", "total_lessons_completed",
            "total_chat_messages", "total_xp_earned", "average_level",
        }
        assert expected == set(ov.keys())

    def test_total_users_single(self, auth_client, user):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["total_users"] == 1

    def test_total_users_multiple(self, auth_client, user, other_user):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["total_users"] == 2

    def test_total_lessons_completed_zero(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["total_lessons_completed"] == 0

    def test_total_lessons_completed(self, auth_client, user, analytics_lesson):
        LessonProgress.objects.create(user=user, lesson=analytics_lesson, completed=True)
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["total_lessons_completed"] == 1

    def test_incomplete_not_counted(self, auth_client, user, analytics_lesson):
        LessonProgress.objects.create(user=user, lesson=analytics_lesson, completed=False)
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["total_lessons_completed"] == 0

    def test_total_chat_messages_zero(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["total_chat_messages"] == 0

    def test_total_chat_messages(self, auth_client, user):
        from chat.models import ChatMessage
        ChatMessage.objects.create(user=user, role="user", content="hi")
        ChatMessage.objects.create(user=user, role="assistant", content="hello")
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["total_chat_messages"] == 2

    def test_total_xp_earned_zero(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["total_xp_earned"] == 0

    def test_total_xp_earned(self, auth_client, user, other_user):
        user.profile.xp = 100
        user.profile.save()
        other_user.profile.xp = 200
        other_user.profile.save()
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["total_xp_earned"] == 300

    def test_average_level_single(self, auth_client, user):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["average_level"] == 1.0

    def test_average_level_multiple(self, auth_client, user, other_user):
        user.profile.level = 3
        user.profile.save()
        other_user.profile.level = 5
        other_user.profile.save()
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["average_level"] == 4.0

    def test_average_level_decimal(self, auth_client, user, other_user, db):
        u3 = User.objects.create_user(username="u3", password="pass")
        user.profile.level = 1
        user.profile.save()
        other_user.profile.level = 2
        other_user.profile.save()
        u3.profile.level = 3
        u3.profile.save()
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["average_level"] == 2.0


class TestAnalyticsXpDistribution:
    def test_returns_list(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert isinstance(resp.data["xp_distribution"], list)

    def test_six_buckets(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert len(resp.data["xp_distribution"]) == 6

    def test_bucket_labels(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        labels = [b["range"] for b in resp.data["xp_distribution"]]
        assert labels == ["0-99", "100-199", "200-299", "300-399", "400-499", "500+"]

    def test_user_in_first_bucket(self, auth_client, user):
        """Default xp=0 → bucket 0-99."""
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["xp_distribution"][0]["count"] == 1

    def test_user_in_500_plus(self, auth_client, user):
        user.profile.xp = 520
        user.profile.save()
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["xp_distribution"][5]["count"] == 1
        # First bucket should be 0
        assert resp.data["xp_distribution"][0]["count"] == 0

    def test_multiple_users_distributed(self, auth_client, user, other_user, db):
        u3 = User.objects.create_user(username="u3", password="pass")
        user.profile.xp = 50
        user.profile.save()
        other_user.profile.xp = 150
        other_user.profile.save()
        u3.profile.xp = 150
        u3.profile.save()
        resp = auth_client.get("/api/v1/analytics/")
        dist = {b["range"]: b["count"] for b in resp.data["xp_distribution"]}
        assert dist["0-99"] == 1
        assert dist["100-199"] == 2

    def test_boundary_99(self, auth_client, user):
        user.profile.xp = 99
        user.profile.save()
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["xp_distribution"][0]["count"] == 1

    def test_boundary_100(self, auth_client, user):
        user.profile.xp = 100
        user.profile.save()
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["xp_distribution"][0]["count"] == 0
        assert resp.data["xp_distribution"][1]["count"] == 1

    def test_empty_db_all_zero(self, db):
        """No users at all → all counts 0."""
        c = APIClient()
        u = User.objects.create_user(username="temp", password="pass")
        c.force_authenticate(user=u)
        resp = c.get("/api/v1/analytics/")
        # Only temp user with xp=0
        assert resp.data["xp_distribution"][0]["count"] == 1
        for bucket in resp.data["xp_distribution"][1:]:
            assert bucket["count"] == 0


class TestAnalyticsPopularLessons:
    def test_returns_list(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert isinstance(resp.data["popular_lessons"], list)

    def test_empty_when_no_lessons(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["popular_lessons"] == []

    def test_lesson_fields(self, auth_client, user, analytics_lesson):
        LessonProgress.objects.create(user=user, lesson=analytics_lesson, completed=True)
        resp = auth_client.get("/api/v1/analytics/")
        entry = resp.data["popular_lessons"][0]
        assert "title" in entry
        assert "path_title" in entry
        assert "completions" in entry
        assert "chat_messages" in entry

    def test_ordered_by_completions(self, auth_client, user, analytics_lesson, analytics_lesson_2):
        LessonProgress.objects.create(user=user, lesson=analytics_lesson, completed=True)
        resp = auth_client.get("/api/v1/analytics/")
        lessons = resp.data["popular_lessons"]
        # analytics_lesson has 1 completion, lesson_2 has 0
        assert lessons[0]["title"] == "A Lesson 1"

    def test_max_5_results(self, auth_client, user, analytics_path):
        for i in range(7):
            Lesson.objects.create(
                path=analytics_path, slug=f"pop-{i}", title=f"Pop {i}",
                xp_reward=10, order=i + 10,
            )
        resp = auth_client.get("/api/v1/analytics/")
        assert len(resp.data["popular_lessons"]) <= 5

    def test_completions_count(self, auth_client, user, other_user, analytics_lesson):
        LessonProgress.objects.create(user=user, lesson=analytics_lesson, completed=True)
        LessonProgress.objects.create(user=other_user, lesson=analytics_lesson, completed=True)
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["popular_lessons"][0]["completions"] == 2

    def test_chat_messages_count(self, auth_client, user, analytics_lesson):
        from chat.models import ChatMessage
        ChatMessage.objects.create(user=user, lesson=analytics_lesson, role="user", content="q")
        ChatMessage.objects.create(user=user, lesson=analytics_lesson, role="assistant", content="a")
        resp = auth_client.get("/api/v1/analytics/")
        entry = next(
            (l for l in resp.data["popular_lessons"] if l["title"] == "A Lesson 1"),
            None,
        )
        assert entry is not None
        assert entry["chat_messages"] == 2

    def test_path_title_included(self, auth_client, user, analytics_lesson):
        LessonProgress.objects.create(user=user, lesson=analytics_lesson, completed=True)
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["popular_lessons"][0]["path_title"] == "Analytics Path"


class TestAnalyticsPathProgress:
    def test_returns_list(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert isinstance(resp.data["path_progress"], list)

    def test_empty_when_no_paths(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["path_progress"] == []

    def test_path_fields(self, auth_client, analytics_path, analytics_lesson):
        resp = auth_client.get("/api/v1/analytics/")
        entry = resp.data["path_progress"][0]
        assert "title" in entry
        assert "icon" in entry
        assert "total_lessons" in entry
        assert "avg_completion_percent" in entry

    def test_total_lessons_count(self, auth_client, analytics_path, analytics_lesson, analytics_lesson_2):
        resp = auth_client.get("/api/v1/analytics/")
        entry = resp.data["path_progress"][0]
        assert entry["total_lessons"] == 2

    def test_zero_completion_percent(self, auth_client, analytics_path, analytics_lesson):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["path_progress"][0]["avg_completion_percent"] == 0

    def test_completion_percent_calculated(self, auth_client, user, analytics_path, analytics_lesson, analytics_lesson_2):
        LessonProgress.objects.create(user=user, lesson=analytics_lesson, completed=True)
        resp = auth_client.get("/api/v1/analytics/")
        # 1 user, 2 lessons, 1 completed → 1/(2*1) * 100 = 50
        assert resp.data["path_progress"][0]["avg_completion_percent"] == 50

    def test_full_completion(self, auth_client, user, analytics_path, analytics_lesson, analytics_lesson_2):
        LessonProgress.objects.create(user=user, lesson=analytics_lesson, completed=True)
        LessonProgress.objects.create(user=user, lesson=analytics_lesson_2, completed=True)
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["path_progress"][0]["avg_completion_percent"] == 100

    def test_avg_across_users(self, auth_client, user, other_user, analytics_path, analytics_lesson, analytics_lesson_2):
        # user completes both, other_user completes none → avg = 50%
        LessonProgress.objects.create(user=user, lesson=analytics_lesson, completed=True)
        LessonProgress.objects.create(user=user, lesson=analytics_lesson_2, completed=True)
        resp = auth_client.get("/api/v1/analytics/")
        # 2 completed / (2 lessons * 2 users) * 100 = 50
        assert resp.data["path_progress"][0]["avg_completion_percent"] == 50

    def test_empty_path_zero_percent(self, auth_client, db):
        LearningPath.objects.create(
            slug="empty-path", title="Empty", description="D",
            icon="X", difficulty="beginner",
        )
        resp = auth_client.get("/api/v1/analytics/")
        entry = next(p for p in resp.data["path_progress"] if p["title"] == "Empty")
        assert entry["avg_completion_percent"] == 0
        assert entry["total_lessons"] == 0


class TestAnalyticsActivity:
    def test_returns_7_days(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert len(resp.data["activity_last_7_days"]) == 7

    def test_day_fields(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        day = resp.data["activity_last_7_days"][0]
        assert "date" in day
        assert "lessons_completed" in day
        assert "chat_messages" in day

    def test_dates_ordered_ascending(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        dates = [d["date"] for d in resp.data["activity_last_7_days"]]
        assert dates == sorted(dates)

    def test_last_day_is_today(self, auth_client):
        from django.utils import timezone
        today = timezone.now().date().isoformat()
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["activity_last_7_days"][-1]["date"] == today

    def test_all_zeros_when_empty(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        for day in resp.data["activity_last_7_days"]:
            assert day["lessons_completed"] == 0
            assert day["chat_messages"] == 0

    def test_today_lesson_counted(self, auth_client, user, analytics_lesson):
        from django.utils import timezone
        LessonProgress.objects.create(
            user=user, lesson=analytics_lesson, completed=True,
            completed_at=timezone.now(),
        )
        resp = auth_client.get("/api/v1/analytics/")
        today_entry = resp.data["activity_last_7_days"][-1]
        assert today_entry["lessons_completed"] == 1

    def test_today_messages_counted(self, auth_client, user):
        from chat.models import ChatMessage
        ChatMessage.objects.create(user=user, role="user", content="hi")
        resp = auth_client.get("/api/v1/analytics/")
        today_entry = resp.data["activity_last_7_days"][-1]
        assert today_entry["chat_messages"] == 1


class TestAnalyticsAchievementsSummary:
    def test_empty_db(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        ach = resp.data["achievements_summary"]
        assert ach["total"] == 0
        assert ach["unlocked_by_anyone"] == 0
        assert ach["most_common"] is None
        assert ach["rarest"] is None

    def test_total_count(self, auth_client, achievement):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["achievements_summary"]["total"] == 1

    def test_unlocked_by_anyone_zero(self, auth_client, achievement):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["achievements_summary"]["unlocked_by_anyone"] == 0

    def test_unlocked_by_anyone(self, auth_client, user, achievement):
        UserAchievement.objects.create(user=user, achievement=achievement)
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["achievements_summary"]["unlocked_by_anyone"] == 1

    def test_most_common_fields(self, auth_client, user, achievement):
        UserAchievement.objects.create(user=user, achievement=achievement)
        resp = auth_client.get("/api/v1/analytics/")
        mc = resp.data["achievements_summary"]["most_common"]
        assert "name" in mc
        assert "icon" in mc
        assert "unlock_count" in mc

    def test_most_common_value(self, auth_client, user, other_user, achievement, db):
        a2 = Achievement.objects.create(
            slug="a2", name="A2", description="D", icon="X",
            requirement_type="streak", requirement_value=1,
        )
        UserAchievement.objects.create(user=user, achievement=achievement)
        UserAchievement.objects.create(user=other_user, achievement=achievement)
        UserAchievement.objects.create(user=user, achievement=a2)
        resp = auth_client.get("/api/v1/analytics/")
        mc = resp.data["achievements_summary"]["most_common"]
        assert mc["name"] == "First Lesson"
        assert mc["unlock_count"] == 2

    def test_rarest_value(self, auth_client, user, achievement, db):
        a2 = Achievement.objects.create(
            slug="rare", name="Rare", description="D", icon="X",
            requirement_type="streak", requirement_value=99,
        )
        UserAchievement.objects.create(user=user, achievement=achievement)
        resp = auth_client.get("/api/v1/analytics/")
        rarest = resp.data["achievements_summary"]["rarest"]
        assert rarest["name"] == "Rare"
        assert rarest["unlock_count"] == 0

    def test_all_achievements_unlocked(self, auth_client, user, achievement):
        UserAchievement.objects.create(user=user, achievement=achievement)
        resp = auth_client.get("/api/v1/analytics/")
        ach = resp.data["achievements_summary"]
        assert ach["unlocked_by_anyone"] == ach["total"]


class TestAnalyticsChatStats:
    def test_fields(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        cs = resp.data["chat_stats"]
        expected = {"total_messages", "avg_messages_per_lesson", "most_active_lesson", "agent_usage"}
        assert expected == set(cs.keys())

    def test_zero_messages(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        cs = resp.data["chat_stats"]
        assert cs["total_messages"] == 0
        assert cs["avg_messages_per_lesson"] == 0
        assert cs["most_active_lesson"] is None

    def test_total_messages(self, auth_client, user):
        from chat.models import ChatMessage
        ChatMessage.objects.create(user=user, role="user", content="q1")
        ChatMessage.objects.create(user=user, role="assistant", content="a1")
        ChatMessage.objects.create(user=user, role="user", content="q2")
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["chat_stats"]["total_messages"] == 3

    def test_avg_messages_per_lesson(self, auth_client, user, analytics_lesson, analytics_lesson_2):
        from chat.models import ChatMessage
        ChatMessage.objects.create(user=user, lesson=analytics_lesson, role="user", content="q1")
        ChatMessage.objects.create(user=user, lesson=analytics_lesson, role="assistant", content="a1")
        ChatMessage.objects.create(user=user, lesson=analytics_lesson_2, role="user", content="q2")
        resp = auth_client.get("/api/v1/analytics/")
        # 3 messages / 2 lessons with chat = 1.5
        assert resp.data["chat_stats"]["avg_messages_per_lesson"] == 1.5

    def test_avg_ignores_null_lesson(self, auth_client, user, analytics_lesson):
        from chat.models import ChatMessage
        ChatMessage.objects.create(user=user, lesson=analytics_lesson, role="user", content="q")
        ChatMessage.objects.create(user=user, lesson=None, role="user", content="free")
        resp = auth_client.get("/api/v1/analytics/")
        # 2 total messages / 1 lesson with chat = 2.0
        assert resp.data["chat_stats"]["avg_messages_per_lesson"] == 2.0

    def test_most_active_lesson(self, auth_client, user, analytics_lesson, analytics_lesson_2):
        from chat.models import ChatMessage
        ChatMessage.objects.create(user=user, lesson=analytics_lesson, role="user", content="q1")
        ChatMessage.objects.create(user=user, lesson=analytics_lesson, role="user", content="q2")
        ChatMessage.objects.create(user=user, lesson=analytics_lesson_2, role="user", content="q3")
        resp = auth_client.get("/api/v1/analytics/")
        mal = resp.data["chat_stats"]["most_active_lesson"]
        assert mal["title"] == "A Lesson 1"
        assert mal["message_count"] == 2

    def test_agent_usage_list(self, auth_client, db):
        from chat.models import ChatAgent
        ChatAgent.objects.create(
            slug="test-agent", name="Test Agent", description="D",
            icon="X", system_prompt="P",
        )
        resp = auth_client.get("/api/v1/analytics/")
        agents = resp.data["chat_stats"]["agent_usage"]
        assert len(agents) == 1
        assert agents[0]["agent"] == "Test Agent"

    def test_agent_usage_empty(self, auth_client):
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["chat_stats"]["agent_usage"] == []

    def test_agent_usage_fields(self, auth_client, db):
        from chat.models import ChatAgent
        ChatAgent.objects.create(
            slug="ag", name="Ag", description="D", icon="\U0001F916",
            system_prompt="P",
        )
        resp = auth_client.get("/api/v1/analytics/")
        agent = resp.data["chat_stats"]["agent_usage"][0]
        assert "agent" in agent
        assert "icon" in agent
        assert "messages" in agent


class TestAnalyticsEdgeCases:
    """Edge cases: empty DB, division by zero, single user."""

    def test_no_division_by_zero_avg_level_empty(self, db):
        """With only the auth user (level=1), no crash."""
        u = User.objects.create_user(username="solo", password="pass")
        c = APIClient()
        c.force_authenticate(user=u)
        resp = c.get("/api/v1/analytics/")
        assert resp.status_code == 200
        assert resp.data["overview"]["average_level"] == 1.0

    def test_no_division_by_zero_avg_messages(self, auth_client):
        """No lessons with chat → avg_messages_per_lesson = 0."""
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["chat_stats"]["avg_messages_per_lesson"] == 0

    def test_no_division_by_zero_path_progress(self, auth_client, db):
        """Path with 0 lessons → avg_completion_percent = 0."""
        LearningPath.objects.create(
            slug="empty", title="Empty", description="D",
            icon="X", difficulty="beginner",
        )
        resp = auth_client.get("/api/v1/analytics/")
        entry = next(p for p in resp.data["path_progress"] if p["title"] == "Empty")
        assert entry["avg_completion_percent"] == 0

    def test_xp_distribution_all_zero_xp(self, auth_client, user):
        resp = auth_client.get("/api/v1/analytics/")
        total = sum(b["count"] for b in resp.data["xp_distribution"])
        assert total == 1  # only the auth user

    def test_large_xp_value(self, auth_client, user):
        user.profile.xp = 99999
        user.profile.save()
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["xp_distribution"][5]["count"] == 1

    def test_concurrent_data_consistency(self, auth_client, user, other_user, analytics_lesson):
        """Overview total_xp matches sum of all profiles."""
        user.profile.xp = 100
        user.profile.save()
        other_user.profile.xp = 200
        other_user.profile.save()
        resp = auth_client.get("/api/v1/analytics/")
        assert resp.data["overview"]["total_xp_earned"] == 300


# ── Email Base Template ──────────────────────────────────


class TestEmailBaseTemplate:
    def test_returns_html_string(self):
        from core.emails import get_email_base_template

        html = get_email_base_template("<p>Test</p>", "Subject")
        assert isinstance(html, str)

    def test_contains_doctype(self):
        from core.emails import get_email_base_template

        html = get_email_base_template("<p>Test</p>", "Subject")
        assert "<!DOCTYPE html>" in html

    def test_contains_subject_in_title(self):
        from core.emails import get_email_base_template

        html = get_email_base_template("<p>Test</p>", "My Subject")
        assert "<title>My Subject</title>" in html

    def test_contains_content(self):
        from core.emails import get_email_base_template

        html = get_email_base_template("<p>Hello World</p>", "Sub")
        assert "<p>Hello World</p>" in html

    def test_contains_branding(self):
        from core.emails import get_email_base_template

        html = get_email_base_template("<p>x</p>", "s")
        assert "AI Learning Hub" in html

    def test_contains_footer(self):
        from core.emails import get_email_base_template

        html = get_email_base_template("<p>x</p>", "s")
        assert "Lernplattform" in html

    def test_dark_theme_colors(self):
        from core.emails import get_email_base_template

        html = get_email_base_template("<p>x</p>", "s")
        assert "#161C24" in html
        assert "#212B36" in html

    def test_primary_color_in_header(self):
        from core.emails import get_email_base_template

        html = get_email_base_template("<p>x</p>", "s")
        assert "#00A76F" in html


# ── Email Helper Functions ───────────────────────────────


class TestEmailHelpers:
    def test_user_email_returns_email(self, user):
        from core.emails import _user_email

        user.email = "test@example.com"
        user.save()
        assert _user_email(user) == "test@example.com"

    def test_user_email_returns_none_if_empty(self, user):
        from core.emails import _user_email

        user.email = ""
        user.save()
        assert _user_email(user) is None

    def test_should_send_true_with_email_and_notifications(self, user):
        from core.emails import _should_send

        user.email = "test@example.com"
        user.save()
        user.profile.email_notifications = True
        user.profile.save()
        assert _should_send(user) is True

    def test_should_send_false_without_email(self, user):
        from core.emails import _should_send

        user.email = ""
        user.save()
        assert _should_send(user) is False

    def test_should_send_false_when_notifications_disabled(self, user):
        from core.emails import _should_send

        user.email = "test@example.com"
        user.save()
        user.profile.email_notifications = False
        user.profile.save()
        assert _should_send(user) is False


# ── Welcome Email ────────────────────────────────────────


class TestWelcomeEmail:
    def test_sends_email(self, user):
        from django.core import mail

        from core.emails import send_welcome_email

        user.email = "test@example.com"
        user.save()
        send_welcome_email(user)
        assert len(mail.outbox) == 1

    def test_subject_contains_willkommen(self, user):
        from django.core import mail

        from core.emails import send_welcome_email

        user.email = "test@example.com"
        user.save()
        send_welcome_email(user)
        assert "Willkommen" in mail.outbox[0].subject

    def test_uses_first_name(self, user):
        from django.core import mail

        from core.emails import send_welcome_email

        user.email = "test@example.com"
        user.first_name = "Max"
        user.save()
        send_welcome_email(user)
        assert "Max" in mail.outbox[0].body

    def test_falls_back_to_username(self, user):
        from django.core import mail

        from core.emails import send_welcome_email

        user.email = "test@example.com"
        user.first_name = ""
        user.save()
        send_welcome_email(user)
        assert user.username in mail.outbox[0].body

    def test_html_content_present(self, user):
        from django.core import mail

        from core.emails import send_welcome_email

        user.email = "test@example.com"
        user.save()
        send_welcome_email(user)
        assert mail.outbox[0].alternatives

    def test_no_email_no_send(self, user):
        from django.core import mail

        from core.emails import send_welcome_email

        user.email = ""
        user.save()
        send_welcome_email(user)
        assert len(mail.outbox) == 0

    def test_recipient_correct(self, user):
        from django.core import mail

        from core.emails import send_welcome_email

        user.email = "max@example.com"
        user.save()
        send_welcome_email(user)
        assert "max@example.com" in mail.outbox[0].to


# ── Achievement Email ────────────────────────────────────


class TestAchievementEmail:
    def test_sends_email(self, user, achievement):
        from django.core import mail

        from core.emails import send_achievement_email

        user.email = "test@example.com"
        user.save()
        send_achievement_email(user, achievement)
        assert len(mail.outbox) == 1

    def test_subject_contains_achievement_name(self, user, achievement):
        from django.core import mail

        from core.emails import send_achievement_email

        user.email = "test@example.com"
        user.save()
        send_achievement_email(user, achievement)
        assert achievement.name in mail.outbox[0].subject

    def test_body_contains_xp(self, user, achievement):
        from django.core import mail

        from core.emails import send_achievement_email

        user.email = "test@example.com"
        user.save()
        send_achievement_email(user, achievement)
        assert str(achievement.xp_reward) in mail.outbox[0].body

    def test_no_send_without_email(self, user, achievement):
        from django.core import mail

        from core.emails import send_achievement_email

        user.email = ""
        user.save()
        send_achievement_email(user, achievement)
        assert len(mail.outbox) == 0

    def test_no_send_when_notifications_disabled(self, user, achievement):
        from django.core import mail

        from core.emails import send_achievement_email

        user.email = "test@example.com"
        user.save()
        user.profile.email_notifications = False
        user.profile.save()
        send_achievement_email(user, achievement)
        assert len(mail.outbox) == 0

    def test_html_contains_achievement_icon(self, user, achievement):
        from django.core import mail

        from core.emails import send_achievement_email

        user.email = "test@example.com"
        user.save()
        send_achievement_email(user, achievement)
        html = mail.outbox[0].alternatives[0][0]
        assert achievement.icon in html


# ── Level Up Email ───────────────────────────────────────


class TestLevelUpEmail:
    def test_sends_email(self, user):
        from django.core import mail

        from core.emails import send_level_up_email

        user.email = "test@example.com"
        user.save()
        send_level_up_email(user, 3, 250)
        assert len(mail.outbox) == 1

    def test_subject_contains_level(self, user):
        from django.core import mail

        from core.emails import send_level_up_email

        user.email = "test@example.com"
        user.save()
        send_level_up_email(user, 3, 250)
        assert "3" in mail.outbox[0].subject

    def test_subject_contains_title(self, user):
        from django.core import mail

        from core.emails import send_level_up_email

        user.email = "test@example.com"
        user.save()
        send_level_up_email(user, 3, 250)
        assert "Fortgeschritten" in mail.outbox[0].subject

    def test_body_contains_xp(self, user):
        from django.core import mail

        from core.emails import send_level_up_email

        user.email = "test@example.com"
        user.save()
        send_level_up_email(user, 3, 250)
        assert "250" in mail.outbox[0].body

    def test_high_level_fallback_title(self, user):
        from django.core import mail

        from core.emails import send_level_up_email

        user.email = "test@example.com"
        user.save()
        send_level_up_email(user, 10, 1000)
        assert "Level 10" in mail.outbox[0].subject

    def test_no_send_without_email(self, user):
        from django.core import mail

        from core.emails import send_level_up_email

        user.email = ""
        user.save()
        send_level_up_email(user, 2, 150)
        assert len(mail.outbox) == 0

    def test_no_send_when_notifications_disabled(self, user):
        from django.core import mail

        from core.emails import send_level_up_email

        user.email = "test@example.com"
        user.save()
        user.profile.email_notifications = False
        user.profile.save()
        send_level_up_email(user, 2, 150)
        assert len(mail.outbox) == 0

    def test_level_1_title(self, user):
        from django.core import mail

        from core.emails import send_level_up_email

        user.email = "test@example.com"
        user.save()
        send_level_up_email(user, 1, 50)
        assert "Anfaenger" in mail.outbox[0].subject


# ── Path Completed Email ─────────────────────────────────


class TestPathCompletedEmail:
    @pytest.fixture
    def path(self, db):
        return LearningPath.objects.create(
            slug="test-path", title="Test Path", icon="T",
            difficulty="beginner", order=1,
        )

    def test_sends_email(self, user, path):
        from django.core import mail

        from core.emails import send_path_completed_email

        user.email = "test@example.com"
        user.save()
        send_path_completed_email(user, path)
        assert len(mail.outbox) == 1

    def test_subject_contains_path_title(self, user, path):
        from django.core import mail

        from core.emails import send_path_completed_email

        user.email = "test@example.com"
        user.save()
        send_path_completed_email(user, path)
        assert path.title in mail.outbox[0].subject

    def test_body_contains_certificate_link(self, user, path):
        from django.core import mail

        from core.emails import send_path_completed_email

        user.email = "test@example.com"
        user.save()
        send_path_completed_email(user, path)
        assert path.slug in mail.outbox[0].body

    def test_html_contains_path_icon(self, user, path):
        from django.core import mail

        from core.emails import send_path_completed_email

        user.email = "test@example.com"
        user.save()
        send_path_completed_email(user, path)
        html = mail.outbox[0].alternatives[0][0]
        assert path.icon in html

    def test_no_send_without_email(self, user, path):
        from django.core import mail

        from core.emails import send_path_completed_email

        user.email = ""
        user.save()
        send_path_completed_email(user, path)
        assert len(mail.outbox) == 0

    def test_no_send_when_notifications_disabled(self, user, path):
        from django.core import mail

        from core.emails import send_path_completed_email

        user.email = "test@example.com"
        user.save()
        user.profile.email_notifications = False
        user.profile.save()
        send_path_completed_email(user, path)
        assert len(mail.outbox) == 0


# ── Streak Reminder Email ────────────────────────────────


class TestStreakReminderEmail:
    def test_sends_email(self, user):
        from django.core import mail

        from core.emails import send_streak_reminder_email

        user.email = "test@example.com"
        user.save()
        send_streak_reminder_email(user, 5)
        assert len(mail.outbox) == 1

    def test_subject_contains_streak_count(self, user):
        from django.core import mail

        from core.emails import send_streak_reminder_email

        user.email = "test@example.com"
        user.save()
        send_streak_reminder_email(user, 12)
        assert "12" in mail.outbox[0].subject

    def test_body_contains_streak_count(self, user):
        from django.core import mail

        from core.emails import send_streak_reminder_email

        user.email = "test@example.com"
        user.save()
        send_streak_reminder_email(user, 7)
        assert "7" in mail.outbox[0].body

    def test_no_send_without_email(self, user):
        from django.core import mail

        from core.emails import send_streak_reminder_email

        user.email = ""
        user.save()
        send_streak_reminder_email(user, 5)
        assert len(mail.outbox) == 0

    def test_no_send_when_notifications_disabled(self, user):
        from django.core import mail

        from core.emails import send_streak_reminder_email

        user.email = "test@example.com"
        user.save()
        user.profile.email_notifications = False
        user.profile.save()
        send_streak_reminder_email(user, 5)
        assert len(mail.outbox) == 0


# ── Email Preview ────────────────────────────────────────


class TestEmailPreview:
    def test_welcome_preview(self):
        from core.emails import get_preview_html

        html = get_preview_html("welcome")
        assert html is not None
        assert "<!DOCTYPE html>" in html
        assert "Hallo" in html

    def test_achievement_preview(self):
        from core.emails import get_preview_html

        html = get_preview_html("achievement")
        assert html is not None
        assert "Erste Schritte" in html

    def test_level_up_preview(self):
        from core.emails import get_preview_html

        html = get_preview_html("level-up")
        assert html is not None
        assert "Level Up" in html

    def test_path_completed_preview(self):
        from core.emails import get_preview_html

        html = get_preview_html("path-completed")
        assert html is not None
        assert "AI Grundlagen" in html

    def test_streak_reminder_preview(self):
        from core.emails import get_preview_html

        html = get_preview_html("streak-reminder")
        assert html is not None
        assert "Streak" in html

    def test_unknown_template_returns_none(self):
        from core.emails import get_preview_html

        assert get_preview_html("nonexistent") is None

    def test_all_previews_contain_branding(self):
        from core.emails import get_preview_html

        for name in ["welcome", "achievement", "level-up", "path-completed", "streak-reminder"]:
            html = get_preview_html(name)
            assert "AI Learning Hub" in html, f"{name} missing branding"

    def test_all_previews_contain_footer(self):
        from core.emails import get_preview_html

        for name in ["welcome", "achievement", "level-up", "path-completed", "streak-reminder"]:
            html = get_preview_html(name)
            assert "Lernplattform" in html, f"{name} missing footer"


# ── Email Notifications Model Field ─────────────────────


class TestEmailNotificationsField:
    def test_default_is_true(self, user):
        assert user.profile.email_notifications is True

    def test_can_set_to_false(self, user):
        user.profile.email_notifications = False
        user.profile.save()
        user.profile.refresh_from_db()
        assert user.profile.email_notifications is False

    def test_can_set_to_true(self, user):
        user.profile.email_notifications = False
        user.profile.save()
        user.profile.email_notifications = True
        user.profile.save()
        user.profile.refresh_from_db()
        assert user.profile.email_notifications is True


# ── Email Preview Endpoint ───────────────────────────────


@pytest.mark.django_db
class TestEmailPreviewEndpoint:
    def test_welcome_returns_html(self, client, settings):
        settings.DEBUG = True
        resp = client.get("/api/v1/email-preview/welcome/")
        assert resp.status_code == 200
        assert resp["Content-Type"] == "text/html"

    def test_achievement_returns_html(self, client, settings):
        settings.DEBUG = True
        resp = client.get("/api/v1/email-preview/achievement/")
        assert resp.status_code == 200

    def test_level_up_returns_html(self, client, settings):
        settings.DEBUG = True
        resp = client.get("/api/v1/email-preview/level-up/")
        assert resp.status_code == 200

    def test_path_completed_returns_html(self, client, settings):
        settings.DEBUG = True
        resp = client.get("/api/v1/email-preview/path-completed/")
        assert resp.status_code == 200

    def test_streak_reminder_returns_html(self, client, settings):
        settings.DEBUG = True
        resp = client.get("/api/v1/email-preview/streak-reminder/")
        assert resp.status_code == 200

    def test_unknown_template_returns_404(self, client, settings):
        settings.DEBUG = True
        resp = client.get("/api/v1/email-preview/nonexistent/")
        assert resp.status_code == 404

    def test_unknown_returns_available_list(self, client, settings):
        settings.DEBUG = True
        resp = client.get("/api/v1/email-preview/nonexistent/")
        assert "available" in resp.data
        assert "welcome" in resp.data["available"]

    def test_html_contains_doctype(self, client, settings):
        settings.DEBUG = True
        resp = client.get("/api/v1/email-preview/welcome/")
        assert b"<!DOCTYPE html>" in resp.content

    def test_html_contains_branding(self, client, settings):
        settings.DEBUG = True
        resp = client.get("/api/v1/email-preview/welcome/")
        assert b"AI Learning Hub" in resp.content

    def test_no_auth_required(self, client, settings):
        """Preview is available without authentication (DEBUG only)."""
        settings.DEBUG = True
        resp = client.get("/api/v1/email-preview/welcome/")
        assert resp.status_code == 200

    def test_returns_403_when_debug_false(self, client, settings):
        """Preview blocked in production."""
        settings.DEBUG = False
        resp = client.get("/api/v1/email-preview/welcome/")
        assert resp.status_code == 403


# ── Email Integration in LessonComplete ──────────────────


class TestEmailIntegration:
    @pytest.fixture
    def email_path(self, db):
        return LearningPath.objects.create(
            slug="email-path", title="Email Path", icon="E",
            difficulty="beginner", order=1,
        )

    @pytest.fixture
    def email_lesson(self, email_path):
        from lessons.models import Lesson

        return Lesson.objects.create(
            path=email_path, slug="email-l1", title="Email L1",
            xp_reward=10, order=1,
        )

    @pytest.fixture
    def email_lesson2(self, email_path):
        from lessons.models import Lesson

        return Lesson.objects.create(
            path=email_path, slug="email-l2", title="Email L2",
            xp_reward=10, order=2,
        )

    def test_level_up_sends_email(self, auth_client, user, email_lesson):
        from django.core import mail

        user.email = "test@example.com"
        user.save()
        # Set XP so completing lesson triggers level up (95 + 10 = 105 → level 2)
        user.profile.xp = 95
        user.profile.level = 1
        user.profile.save()
        auth_client.post(f"/api/v1/lessons/{email_lesson.slug}/complete/")
        level_emails = [m for m in mail.outbox if "Level" in m.subject]
        assert len(level_emails) == 1

    def test_no_level_up_no_email(self, auth_client, user, email_lesson):
        from django.core import mail

        user.email = "test@example.com"
        user.save()
        # XP stays within same level
        user.profile.xp = 0
        user.profile.level = 1
        user.profile.save()
        auth_client.post(f"/api/v1/lessons/{email_lesson.slug}/complete/")
        level_emails = [m for m in mail.outbox if "Level" in m.subject]
        assert len(level_emails) == 0

    def test_path_completed_sends_email(self, auth_client, user, email_path, email_lesson):
        from django.core import mail

        user.email = "test@example.com"
        user.save()
        # Path has only 1 lesson, completing it finishes the path
        auth_client.post(f"/api/v1/lessons/{email_lesson.slug}/complete/")
        path_emails = [m for m in mail.outbox if "Lernpfad" in m.subject]
        assert len(path_emails) == 1

    def test_path_not_completed_no_email(self, auth_client, user, email_path, email_lesson, email_lesson2):
        from django.core import mail

        user.email = "test@example.com"
        user.save()
        # Path has 2 lessons, completing 1 doesn't finish it
        auth_client.post(f"/api/v1/lessons/{email_lesson.slug}/complete/")
        path_emails = [m for m in mail.outbox if "Lernpfad" in m.subject]
        assert len(path_emails) == 0

    def test_achievement_sends_email(self, auth_client, user, email_lesson):
        from django.core import mail

        user.email = "test@example.com"
        user.save()
        Achievement.objects.create(
            slug="test-ach-email", name="Test Ach", description="Test",
            icon="T", xp_reward=10, requirement_type="lessons_completed",
            requirement_value=1,
        )
        auth_client.post(f"/api/v1/lessons/{email_lesson.slug}/complete/")
        ach_emails = [m for m in mail.outbox if "Achievement" in m.subject]
        assert len(ach_emails) == 1

    def test_no_email_without_user_email(self, auth_client, user, email_lesson):
        from django.core import mail

        user.email = ""
        user.save()
        user.profile.xp = 95
        user.profile.level = 1
        user.profile.save()
        auth_client.post(f"/api/v1/lessons/{email_lesson.slug}/complete/")
        assert len(mail.outbox) == 0

    def test_no_email_when_notifications_disabled(self, auth_client, user, email_lesson):
        from django.core import mail

        user.email = "test@example.com"
        user.save()
        user.profile.email_notifications = False
        user.profile.xp = 95
        user.profile.level = 1
        user.profile.save()
        auth_client.post(f"/api/v1/lessons/{email_lesson.slug}/complete/")
        # No level-up or path-completed emails
        assert len(mail.outbox) == 0

    def test_already_completed_no_emails(self, auth_client, user, email_lesson):
        from django.core import mail

        user.email = "test@example.com"
        user.save()
        # Complete once
        auth_client.post(f"/api/v1/lessons/{email_lesson.slug}/complete/")
        mail.outbox.clear()
        # Complete again — should not send any new emails
        auth_client.post(f"/api/v1/lessons/{email_lesson.slug}/complete/")
        assert len(mail.outbox) == 0
