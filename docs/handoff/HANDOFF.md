# Handoff — AI Learning Hub

## Current State
- Django backend with models, migrations, admin, seed data, and 224 tests
- React + Vite frontend with MUI Dark Theme, routing, layout, dashboard, chat with agent selection
- 4 learning paths (17 lessons), 5 achievements, 2 chat agents seeded

## Backend Structure
- `backend/` — Django project `ai_learning_hub`
- Apps: `core`, `lessons`, `chat`
- Packages: Django 6.0, DRF, django-cors-headers, anthropic, python-dotenv, pytest, ruff
- Config: CORS enabled, DRF with Basic+Session auth, SQLite, dotenv loaded

### Models
- **core:** UserProfile (auto-created via signal, XP, level, streak, avatar_color), Achievement (slug, requirement_type/value, xp_reward), UserAchievement (unique_together user+achievement)
- **lessons:** LearningPath (slug, difficulty, order), Lesson (FK to path, content, ai_system_prompt, xp_reward), LessonProgress (unique_together user+lesson, completed, completed_at)
- **chat:** ChatAgent (slug unique, name, description, icon, system_prompt, color), ChatMessage (FK user CASCADE, FK lesson SET_NULL, role user/assistant, ordering by created_at)

### API Endpoints
- `GET /api/v1/paths/` — List learning paths
- `GET /api/v1/paths/<slug>/` — Path detail with lessons
- `GET /api/v1/lessons/<slug>/` — Lesson detail
- `POST /api/v1/lessons/<slug>/complete/` — Complete lesson
- `POST /api/v1/chat/` — Send chat message (supports lesson_id and agent_slug)
- `GET /api/v1/chat/agents/` — List chat agents (public)
- `GET /api/v1/profile/` — User profile
- `GET /api/v1/leaderboard/` — Leaderboard (public)
- `GET /api/v1/achievements/` — User achievements
- `POST /api/v1/auth/login/` — Login
- `GET /api/v1/auth/demo-users/` — Demo users (public)

### Seed Data
- 4 learning paths: AI Grundlagen (4), Prompt Engineering (3), Agentic Workflows (5), AI in Finance (5)
- 5 achievements: first-lesson, first-chat, three-streak, all-basics, xp-100
- 2 chat agents: general (AI Tutor), finance (Finance AI)
- 3 demo users: demo (Gina M.), anna (Anna M., xp=520), marco (Marco L., xp=410)

### Tests — 224 passing
- core: 73 (UserProfile, Achievement, UserAchievement, API)
- lessons: 67 (LearningPath, Lesson, LessonProgress, API)
- chat: 84 (ChatMessage 18, ChatAPI 17, ChatAchievement 7, ChatAgent model 13, Agents API 9, Chat with Agent 11, + management cmd tests)

## Frontend Structure
- `frontend/` — React 18 + Vite + TypeScript
- MUI v5 Dark Theme with custom palette
- DashboardLayout: collapsible sidebar with active indicator
- ChatPage: Agent selection via Chips, ChatPanel with agentSlug prop
- Routes: `/` `/learn` `/learn/:pathSlug/:lessonSlug` `/leaderboard` `/profile` `/achievements` `/chat`

## Chat Agent Feature
- ChatAgent model with slug, name, description, icon, system_prompt, color
- `agent_slug` parameter in chat API — agent prompt used unless lesson has its own prompt
- Frontend ChatPage shows agent Chips when multiple agents exist
- `key={selectedAgent}` on ChatPanel resets chat history when switching agents

## Next Steps
- Add more specialized agents (e.g., Code AI, Ethics AI)
- Agent-specific chat history (currently shared per user+lesson)
- Frontend: Dashboard card for "AI in Finance" learning path
- Code splitting for bundle size optimization
