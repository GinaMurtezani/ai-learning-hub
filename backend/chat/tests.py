from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.test import APIClient

from chat.models import ChatAgent, ChatMessage
from core.models import Achievement, UserAchievement
from lessons.models import Lesson, LearningPath


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
        description="D",
        icon="X",
        difficulty="beginner",
    )


@pytest.fixture
def lesson(learning_path):
    return Lesson.objects.create(
        path=learning_path,
        slug="intro-ai",
        title="Intro to AI",
        ai_system_prompt="Du bist ein AI-Tutor.",
    )


@pytest.fixture
def lesson_no_prompt(learning_path):
    return Lesson.objects.create(
        path=learning_path,
        slug="no-prompt",
        title="No Prompt Lesson",
        ai_system_prompt="",
    )


@pytest.fixture
def user_message(user, lesson):
    return ChatMessage.objects.create(
        user=user, lesson=lesson, role="user", content="Hello AI"
    )


@pytest.fixture
def assistant_message(user, lesson):
    return ChatMessage.objects.create(
        user=user, lesson=lesson, role="assistant", content="Hello! How can I help?"
    )


@pytest.fixture
def first_chat_achievement(db):
    return Achievement.objects.create(
        slug="first-chat",
        name="Erste Frage",
        description="Stelle deine erste Frage",
        icon="\U0001F4AC",
        xp_reward=15,
        requirement_type="first_chat",
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


def _mock_anthropic_response(text="Mocked AI response"):
    """Create a mock Anthropic messages.create response."""
    mock_content = MagicMock()
    mock_content.text = text
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    return mock_response


# ── ChatMessage Model ───────────────────────────────────────


class TestChatMessage:
    def test_create_user_message(self, user_message):
        assert user_message.pk is not None

    def test_create_assistant_message(self, assistant_message):
        assert assistant_message.pk is not None

    def test_str_format(self, user_message):
        s = str(user_message)
        assert "testuser" in s
        assert "user" in s

    def test_role_user(self, user_message):
        assert user_message.role == "user"

    def test_role_assistant(self, assistant_message):
        assert assistant_message.role == "assistant"

    def test_content_stored(self, user_message):
        assert user_message.content == "Hello AI"

    def test_created_at_auto_set(self, user_message):
        assert user_message.created_at is not None

    def test_ordering_by_created_at(self, user_message, assistant_message):
        messages = list(ChatMessage.objects.all())
        assert messages[0].created_at <= messages[1].created_at

    def test_lesson_nullable(self, user):
        msg = ChatMessage.objects.create(
            user=user, lesson=None, role="user", content="General question"
        )
        assert msg.lesson is None

    def test_lesson_set_null_on_delete(self, user_message, lesson):
        msg_id = user_message.id
        lesson.delete()
        user_message.refresh_from_db()
        assert ChatMessage.objects.get(id=msg_id).lesson is None

    def test_cascade_delete_user(self, user_message, user):
        user.delete()
        assert ChatMessage.objects.count() == 0

    def test_related_name_from_user(self, user, user_message):
        assert user_message in user.chat_messages.all()

    def test_related_name_from_lesson(self, lesson, user_message):
        assert user_message in lesson.chat_messages.all()

    def test_long_content(self, user, lesson):
        long_content = "A" * 10000
        msg = ChatMessage.objects.create(
            user=user, lesson=lesson, role="user", content=long_content
        )
        msg.refresh_from_db()
        assert len(msg.content) == 10000

    def test_multiple_messages_per_user(self, user, lesson):
        ChatMessage.objects.create(user=user, lesson=lesson, role="user", content="Q1")
        ChatMessage.objects.create(user=user, lesson=lesson, role="user", content="Q2")
        assert user.chat_messages.count() == 2

    def test_user_fk_required(self, lesson):
        with pytest.raises(IntegrityError):
            ChatMessage.objects.create(
                user=None, lesson=lesson, role="user", content="No user"
            )

    def test_different_users_same_lesson(self, user, other_user, lesson):
        ChatMessage.objects.create(user=user, lesson=lesson, role="user", content="A")
        msg2 = ChatMessage.objects.create(
            user=other_user, lesson=lesson, role="user", content="B"
        )
        assert msg2.pk is not None

    def test_messages_without_lesson(self, user):
        m1 = ChatMessage.objects.create(user=user, role="user", content="Q")
        m2 = ChatMessage.objects.create(user=user, role="assistant", content="A")
        assert m1.lesson is None
        assert m2.lesson is None


# ── Chat API ────────────────────────────────────────────────


@pytest.fixture
def mock_anthropic():
    with patch("chat.views.Anthropic") as mock_cls, \
         patch("chat.views.os.getenv", return_value="sk-ant-test-key"):
        mock_instance = MagicMock()
        mock_instance.messages.create.return_value = _mock_anthropic_response()
        mock_cls.return_value = mock_instance
        yield mock_instance


class TestChatAPI:
    def test_chat_success(self, auth_client, lesson, mock_anthropic):
        resp = auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "lesson_id": lesson.id}
        )
        assert resp.status_code == 200
        assert resp.data["response"] == "Mocked AI response"

    def test_chat_saves_user_message(self, auth_client, user, lesson, mock_anthropic):
        auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "lesson_id": lesson.id}
        )
        msgs = ChatMessage.objects.filter(user=user, role="user")
        assert msgs.count() == 1
        assert msgs.first().content == "Hello"

    def test_chat_saves_assistant_message(self, auth_client, user, lesson, mock_anthropic):
        auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "lesson_id": lesson.id}
        )
        msgs = ChatMessage.objects.filter(user=user, role="assistant")
        assert msgs.count() == 1
        assert msgs.first().content == "Mocked AI response"

    def test_chat_without_lesson(self, auth_client, mock_anthropic):
        resp = auth_client.post("/api/v1/chat/", {"message": "General question"})
        assert resp.status_code == 200
        assert resp.data["lesson_id"] is None

    def test_chat_invalid_lesson_id(self, auth_client, mock_anthropic):
        resp = auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "lesson_id": 99999}
        )
        assert resp.status_code == 404

    def test_chat_unauthenticated(self, client, mock_anthropic):
        resp = client.post("/api/v1/chat/", {"message": "Hello"})
        assert resp.status_code in (401, 403)

    def test_chat_missing_message(self, auth_client, mock_anthropic):
        resp = auth_client.post("/api/v1/chat/", {})
        assert resp.status_code == 400

    def test_chat_empty_message(self, auth_client, mock_anthropic):
        resp = auth_client.post("/api/v1/chat/", {"message": ""})
        assert resp.status_code == 400

    def test_chat_returns_lesson_id(self, auth_client, lesson, mock_anthropic):
        resp = auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "lesson_id": lesson.id}
        )
        assert resp.data["lesson_id"] == lesson.id

    def test_chat_message_linked_to_lesson(self, auth_client, user, lesson, mock_anthropic):
        auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "lesson_id": lesson.id}
        )
        msg = ChatMessage.objects.filter(user=user, role="user").first()
        assert msg.lesson == lesson

    def test_chat_multiple_messages(self, auth_client, user, lesson, mock_anthropic):
        auth_client.post("/api/v1/chat/", {"message": "Q1", "lesson_id": lesson.id})
        auth_client.post("/api/v1/chat/", {"message": "Q2", "lesson_id": lesson.id})
        assert ChatMessage.objects.filter(user=user).count() == 4  # 2 user + 2 assistant

    def test_chat_uses_lesson_system_prompt(self, auth_client, lesson, mock_anthropic):
        auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "lesson_id": lesson.id}
        )
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert call_kwargs["system"] == "Du bist ein AI-Tutor."

    def test_chat_uses_default_prompt_without_lesson(self, auth_client, mock_anthropic):
        auth_client.post("/api/v1/chat/", {"message": "Hello"})
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert "AI Learning Hub" in call_kwargs["system"]

    def test_chat_uses_default_prompt_when_lesson_has_empty_prompt(
        self, auth_client, lesson_no_prompt, mock_anthropic
    ):
        auth_client.post(
            "/api/v1/chat/",
            {"message": "Hello", "lesson_id": lesson_no_prompt.id},
        )
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert "AI Learning Hub" in call_kwargs["system"]

    def test_chat_sends_history(self, auth_client, user, lesson, mock_anthropic):
        # Pre-create some messages
        ChatMessage.objects.create(user=user, lesson=lesson, role="user", content="Old Q")
        ChatMessage.objects.create(
            user=user, lesson=lesson, role="assistant", content="Old A"
        )
        auth_client.post(
            "/api/v1/chat/", {"message": "New Q", "lesson_id": lesson.id}
        )
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        messages = call_kwargs["messages"]
        assert len(messages) == 3  # Old Q, Old A, New Q
        assert messages[0]["content"] == "Old Q"
        assert messages[1]["content"] == "Old A"
        assert messages[2]["content"] == "New Q"

    def test_chat_history_max_20(self, auth_client, user, lesson, mock_anthropic):
        # Create 25 messages
        for i in range(25):
            role = "user" if i % 2 == 0 else "assistant"
            ChatMessage.objects.create(
                user=user, lesson=lesson, role=role, content=f"Msg {i}"
            )
        auth_client.post(
            "/api/v1/chat/", {"message": "Latest", "lesson_id": lesson.id}
        )
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        messages = call_kwargs["messages"]
        # 20 history + 1 new = 21
        assert len(messages) == 21

    def test_chat_calls_correct_model(self, auth_client, lesson, mock_anthropic):
        auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "lesson_id": lesson.id}
        )
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-sonnet-4-20250514"
        assert call_kwargs["max_tokens"] == 1024

    def test_chat_returns_new_achievements(self, auth_client, mock_anthropic):
        resp = auth_client.post("/api/v1/chat/", {"message": "Hello"})
        assert "new_achievements" in resp.data

    def test_chat_missing_api_key(self, auth_client, lesson, settings):
        settings.ANTHROPIC_API_KEY = None
        with patch("chat.views.os.getenv", return_value=None):
            resp = auth_client.post(
                "/api/v1/chat/", {"message": "Hello", "lesson_id": lesson.id}
            )
            assert resp.status_code == 500
            assert "ANTHROPIC_API_KEY" in resp.data["error"]

    def test_chat_anthropic_api_error(self, auth_client, lesson):
        from anthropic import APIStatusError

        with patch("chat.views.Anthropic") as mock_cls, \
             patch("chat.views.os.getenv", return_value="sk-ant-test-key"):
            mock_instance = MagicMock()
            mock_error = APIStatusError(
                message="Rate limited",
                response=MagicMock(status_code=429),
                body={"error": {"message": "Rate limited"}},
            )
            mock_instance.messages.create.side_effect = mock_error
            mock_cls.return_value = mock_instance
            resp = auth_client.post(
                "/api/v1/chat/", {"message": "Hello", "lesson_id": lesson.id}
            )
            assert resp.status_code == 502


# ── Chat Achievement ────────────────────────────────────────


class TestChatAchievement:
    def test_first_chat_unlocks_achievement(
        self, auth_client, user, first_chat_achievement, mock_anthropic
    ):
        resp = auth_client.post("/api/v1/chat/", {"message": "Hello"})
        assert len(resp.data["new_achievements"]) == 1
        assert resp.data["new_achievements"][0]["name"] == "Erste Frage"

    def test_first_chat_achievement_awards_xp(
        self, auth_client, user, first_chat_achievement, mock_anthropic
    ):
        auth_client.post("/api/v1/chat/", {"message": "Hello"})
        user.profile.refresh_from_db()
        assert user.profile.xp == 15

    def test_first_chat_achievement_not_duplicated(
        self, auth_client, user, first_chat_achievement, mock_anthropic
    ):
        auth_client.post("/api/v1/chat/", {"message": "Hello"})
        resp = auth_client.post("/api/v1/chat/", {"message": "Hello again"})
        assert len(resp.data["new_achievements"]) == 0
        assert UserAchievement.objects.filter(user=user).count() == 1

    def test_first_chat_achievement_xp_not_doubled(
        self, auth_client, user, first_chat_achievement, mock_anthropic
    ):
        auth_client.post("/api/v1/chat/", {"message": "Hello"})
        auth_client.post("/api/v1/chat/", {"message": "Hello again"})
        user.profile.refresh_from_db()
        assert user.profile.xp == 15

    def test_no_achievement_without_seed(self, auth_client, mock_anthropic):
        resp = auth_client.post("/api/v1/chat/", {"message": "Hello"})
        assert resp.data["new_achievements"] == []

    def test_first_chat_achievement_contains_icon(
        self, auth_client, first_chat_achievement, mock_anthropic
    ):
        resp = auth_client.post("/api/v1/chat/", {"message": "Hello"})
        assert resp.data["new_achievements"][0]["icon"] == "\U0001F4AC"

    def test_first_chat_achievement_contains_xp_reward(
        self, auth_client, first_chat_achievement, mock_anthropic
    ):
        resp = auth_client.post("/api/v1/chat/", {"message": "Hello"})
        assert resp.data["new_achievements"][0]["xp_reward"] == 15


# ── ChatAgent Model ────────────────────────────────────────


@pytest.fixture
def general_agent(db):
    return ChatAgent.objects.create(
        slug="general",
        name="AI Tutor",
        description="Allgemeiner AI-Tutor",
        icon="\U0001F916",
        system_prompt="Du bist ein allgemeiner AI-Tutor.",
        color="#00A76F",
    )


@pytest.fixture
def finance_agent(db):
    return ChatAgent.objects.create(
        slug="finance",
        name="Finance AI",
        description="Finance AI Agent",
        icon="\U0001F4B9",
        system_prompt="Du bist ein Finance-AI-Experte.",
        color="#FFC107",
    )


class TestChatAgentModel:
    def test_create_agent(self, general_agent):
        assert general_agent.pk is not None

    def test_slug_unique(self, general_agent, db):
        with pytest.raises(IntegrityError):
            ChatAgent.objects.create(
                slug="general",
                name="Duplicate",
                description="D",
                icon="X",
                system_prompt="P",
            )

    def test_str(self, general_agent):
        assert str(general_agent) == "AI Tutor"

    def test_name_field(self, general_agent):
        assert general_agent.name == "AI Tutor"

    def test_description_field(self, general_agent):
        assert general_agent.description == "Allgemeiner AI-Tutor"

    def test_icon_field(self, general_agent):
        assert general_agent.icon == "\U0001F916"

    def test_system_prompt_field(self, general_agent):
        assert "allgemeiner AI-Tutor" in general_agent.system_prompt

    def test_color_default(self, db):
        agent = ChatAgent.objects.create(
            slug="test-default",
            name="Test",
            description="D",
            icon="X",
            system_prompt="P",
        )
        assert agent.color == "#00A76F"

    def test_color_custom(self, finance_agent):
        assert finance_agent.color == "#FFC107"

    def test_multiple_agents(self, general_agent, finance_agent):
        assert ChatAgent.objects.count() == 2

    def test_slug_max_length(self, db):
        agent = ChatAgent.objects.create(
            slug="a" * 50,
            name="Long Slug",
            description="D",
            icon="X",
            system_prompt="P",
        )
        assert agent.pk is not None

    def test_name_max_length(self, db):
        agent = ChatAgent.objects.create(
            slug="long-name",
            name="N" * 200,
            description="D",
            icon="X",
            system_prompt="P",
        )
        assert len(agent.name) == 200

    def test_long_system_prompt(self, db):
        long_prompt = "X" * 5000
        agent = ChatAgent.objects.create(
            slug="long-prompt",
            name="Agent",
            description="D",
            icon="X",
            system_prompt=long_prompt,
        )
        agent.refresh_from_db()
        assert len(agent.system_prompt) == 5000

    def test_long_description(self, db):
        long_desc = "D" * 5000
        agent = ChatAgent.objects.create(
            slug="long-desc",
            name="Agent",
            description=long_desc,
            icon="X",
            system_prompt="P",
        )
        agent.refresh_from_db()
        assert len(agent.description) == 5000


# ── Chat Agents API ────────────────────────────────────────


class TestChatAgentsAPI:
    def test_list_agents(self, client, general_agent, finance_agent):
        resp = client.get("/api/v1/chat/agents/")
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_list_agents_empty(self, client, db):
        resp = client.get("/api/v1/chat/agents/")
        assert resp.status_code == 200
        assert len(resp.data) == 0

    def test_list_agents_unauthenticated(self, client, general_agent):
        resp = client.get("/api/v1/chat/agents/")
        assert resp.status_code == 200

    def test_agent_fields(self, client, general_agent):
        resp = client.get("/api/v1/chat/agents/")
        agent = resp.data[0]
        assert "slug" in agent
        assert "name" in agent
        assert "description" in agent
        assert "icon" in agent
        assert "color" in agent

    def test_agent_excludes_system_prompt(self, client, general_agent):
        resp = client.get("/api/v1/chat/agents/")
        agent = resp.data[0]
        assert "system_prompt" not in agent

    def test_agent_slug_value(self, client, general_agent):
        resp = client.get("/api/v1/chat/agents/")
        agent = resp.data[0]
        assert agent["slug"] == "general"

    def test_agent_name_value(self, client, general_agent):
        resp = client.get("/api/v1/chat/agents/")
        agent = resp.data[0]
        assert agent["name"] == "AI Tutor"

    def test_agent_color_value(self, client, general_agent):
        resp = client.get("/api/v1/chat/agents/")
        agent = resp.data[0]
        assert agent["color"] == "#00A76F"

    def test_agents_ordered(self, client, general_agent, finance_agent):
        resp = client.get("/api/v1/chat/agents/")
        slugs = [a["slug"] for a in resp.data]
        assert len(slugs) == 2


# ── Chat with Agent ────────────────────────────────────────


class TestChatWithAgent:
    def test_chat_with_agent_slug(self, auth_client, finance_agent, mock_anthropic):
        resp = auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "agent_slug": "finance"}
        )
        assert resp.status_code == 200

    def test_chat_agent_uses_agent_prompt(
        self, auth_client, finance_agent, mock_anthropic
    ):
        auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "agent_slug": "finance"}
        )
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert "Finance-AI-Experte" in call_kwargs["system"]

    def test_chat_agent_invalid_slug(self, auth_client, mock_anthropic):
        resp = auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "agent_slug": "nonexistent"}
        )
        assert resp.status_code == 404

    def test_chat_lesson_prompt_overrides_agent(
        self, auth_client, lesson, finance_agent, mock_anthropic
    ):
        resp = auth_client.post(
            "/api/v1/chat/",
            {"message": "Hello", "lesson_id": lesson.id, "agent_slug": "finance"},
        )
        assert resp.status_code == 200
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert call_kwargs["system"] == "Du bist ein AI-Tutor."

    def test_chat_agent_with_empty_lesson_prompt(
        self, auth_client, lesson_no_prompt, finance_agent, mock_anthropic
    ):
        auth_client.post(
            "/api/v1/chat/",
            {"message": "Hello", "lesson_id": lesson_no_prompt.id, "agent_slug": "finance"},
        )
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert "Finance-AI-Experte" in call_kwargs["system"]

    def test_chat_without_agent_uses_default(self, auth_client, mock_anthropic):
        auth_client.post("/api/v1/chat/", {"message": "Hello"})
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert "AI Learning Hub" in call_kwargs["system"]

    def test_chat_agent_saves_messages(
        self, auth_client, user, finance_agent, mock_anthropic
    ):
        auth_client.post(
            "/api/v1/chat/", {"message": "Finance Q", "agent_slug": "finance"}
        )
        assert ChatMessage.objects.filter(user=user, role="user").count() == 1
        assert ChatMessage.objects.filter(user=user, role="assistant").count() == 1

    def test_chat_agent_returns_response(
        self, auth_client, finance_agent, mock_anthropic
    ):
        resp = auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "agent_slug": "finance"}
        )
        assert resp.data["response"] == "Mocked AI response"

    def test_chat_agent_returns_achievements(
        self, auth_client, finance_agent, first_chat_achievement, mock_anthropic
    ):
        resp = auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "agent_slug": "finance"}
        )
        assert len(resp.data["new_achievements"]) == 1

    def test_chat_general_agent_uses_agent_prompt(
        self, auth_client, general_agent, mock_anthropic
    ):
        auth_client.post(
            "/api/v1/chat/", {"message": "Hello", "agent_slug": "general"}
        )
        call_kwargs = mock_anthropic.messages.create.call_args.kwargs
        assert "allgemeiner AI-Tutor" in call_kwargs["system"]

    def test_chat_agent_unauthenticated(self, client, finance_agent, mock_anthropic):
        resp = client.post(
            "/api/v1/chat/", {"message": "Hello", "agent_slug": "finance"}
        )
        assert resp.status_code in (401, 403)
