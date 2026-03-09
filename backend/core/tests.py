import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.test import APIClient

from core.models import Achievement, UserAchievement, UserProfile


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
