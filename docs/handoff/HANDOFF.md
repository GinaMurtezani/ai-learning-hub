# Handoff — AI Learning Hub

## Current State
- Django backend with models, migrations, admin, seed data, and 224 tests
- React + Vite frontend with MUI Dark Theme, full gamification UI, all pages connected to real API
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
- `GET /api/v1/paths/` — List learning paths (with nested lessons + per-lesson completion status)
- `GET /api/v1/paths/<slug>/` — Path detail with lessons
- `GET /api/v1/lessons/<slug>/` — Lesson detail
- `POST /api/v1/lessons/<slug>/complete/` — Complete lesson
- `POST /api/v1/chat/` — Send chat message (supports lesson_id and agent_slug)
- `GET /api/v1/chat/agents/` — List chat agents (public)
- `GET /api/v1/profile/` — User profile
- `GET /api/v1/leaderboard/` — Leaderboard with display_name, streak_days (public)
- `GET /api/v1/achievements/` — User achievements with progress (current/target per achievement)
- `GET /api/v1/analytics/` — Analytics dashboard (overview, xp distribution, popular lessons, path progress, activity 7d, achievements summary, chat stats)
- `POST /api/v1/auth/login/` — Login
- `GET /api/v1/auth/demo-users/` — Demo users (public)

### Serializers (notable additions)
- **LeaderboardSerializer**: includes `display_name` (first+last name or username) and `streak_days`
- **AchievementWithUnlockSerializer**: includes `progress` field `{current, target}` per achievement
- **LessonWithProgressSerializer**: includes `completed` boolean per lesson
- **LearningPathListSerializer**: now includes nested `lessons` with completion status

### Seed Data
- 4 learning paths: AI Grundlagen (4), Prompt Engineering (3), Agentic Workflows (5), AI in Finance (5)
- 5 achievements: first-lesson, first-chat, three-streak, all-basics, xp-100
- 2 chat agents: general (AI Tutor), finance (Finance AI)
- 3 demo users: demo (Gina M.), anna (Anna M., xp=520), marco (Marco L., xp=410)

### Tests — 349 passing
- core: 145 (UserProfile, Achievement, UserAchievement, API, Leaderboard display_name, Achievement progress, Analytics 72)
- lessons: 86 (LearningPath, Lesson, LessonProgress, API, PathListLessonsField 19)
- chat: 84 (ChatMessage 18, ChatAPI 17, ChatAchievement 7, ChatAgent model 13, Agents API 9, Chat with Agent 11, + management cmd tests)

## Frontend Structure
- `frontend/` — React 19 + Vite + TypeScript
- MUI v5 Dark Theme with custom palette
- Framer Motion animations on all pages (fade+slideUp, stagger)
- DashboardLayout: collapsible sidebar with active indicator
- Routes: `/` `/learn` `/learn/:pathSlug/:lessonSlug` `/leaderboard` `/analytics` `/profile` `/achievements` `/chat`

### Pages (all connected to real API)
- **DashboardPage**: StatCards (Level, XP, Streak, Missions) from API, learning paths with progress, leaderboard top 5, "Next Mission" card — all with Skeleton loading
- **LeaderboardPage**: Full table with Top-3 medals, own row highlighted, Level chips, animated XP CountUp, streak display, stagger animations
- **AchievementsPage**: Grid with unlocked (glow, date) / locked (grayscale, progress bar) states, stats header with progress bar
- **ProfilePage**: 2-column layout — avatar + info left, XP bar + streak calendar (30-day grid) + recent achievements + learning progress right
- **LearningPathsPage**: All paths with nested lesson list, completion icons (check/pulse/dot), difficulty chips, progress bars, click-to-navigate
- **LessonPage**: Markdown content + ChatPanel, breadcrumbs, completion button with XP reward
- **AnalyticsPage**: Recharts dashboard — AreaChart (7d activity), BarChart (popular lessons, XP distribution), PieChart (chat donut), path progress bars, achievement highlights, 6 mini stat cards with CountUp
- **ChatPage**: Agent selection via Chips, ChatPanel with agentSlug
- **LoginPage**: Demo user tiles with one-click login, manual login expandable

## Chat Agent Feature
- ChatAgent model with slug, name, description, icon, system_prompt, color
- `agent_slug` parameter in chat API — agent prompt used unless lesson has its own prompt
- Frontend ChatPage shows agent Chips when multiple agents exist
- `key={selectedAgent}` on ChatPanel resets chat history when switching agents

## Next Steps
- Add more specialized agents (e.g., Code AI, Ethics AI)
- Agent-specific chat history (currently shared per user+lesson)
- Code splitting for bundle size optimization
- Real daily activity tracking for streak calendar (currently uses streak_days count)
- Backend tests for new serializer fields (progress, display_name, lessons with completion)
