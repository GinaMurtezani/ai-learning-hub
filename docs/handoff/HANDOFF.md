# Handoff — AI Learning Hub

## Current State
- Django backend with models, migrations, admin, seed data, and 471 tests
- React + Vite frontend with MUI Dark Theme, full gamification UI, all pages connected to real API
- 4 learning paths (17 lessons), 5 achievements, 2 chat agents seeded
- PDF certificate generation, email notification system

## Backend Structure
- `backend/` — Django project `ai_learning_hub`
- Apps: `core`, `lessons`, `chat`
- Packages: Django 6.0, DRF, django-cors-headers, anthropic, python-dotenv, pytest, ruff, reportlab
- Config: CORS enabled, DRF with Basic+Session auth, SQLite, dotenv loaded, email (console backend)

### Models
- **core:** UserProfile (auto-created via signal, XP, level, streak, avatar_color, email_notifications), Achievement (slug, requirement_type/value, xp_reward), UserAchievement (unique_together user+achievement)
- **lessons:** LearningPath (slug, difficulty, order), Lesson (FK to path, content, ai_system_prompt, xp_reward), LessonProgress (unique_together user+lesson, completed, completed_at)
- **chat:** ChatAgent (slug unique, name, description, icon, system_prompt, color), ChatMessage (FK user CASCADE, FK lesson SET_NULL, role user/assistant, ordering by created_at)

### API Endpoints
- `GET /api/v1/paths/` — List learning paths (with nested lessons + per-lesson completion status)
- `GET /api/v1/paths/<slug>/` — Path detail with lessons
- `GET /api/v1/paths/<slug>/certificate/` — Download PDF certificate (requires all lessons completed)
- `GET /api/v1/lessons/<slug>/` — Lesson detail
- `POST /api/v1/lessons/<slug>/complete/` — Complete lesson (triggers level-up, achievement, path-complete emails)
- `POST /api/v1/chat/` — Send chat message (supports lesson_id and agent_slug)
- `GET /api/v1/chat/agents/` — List chat agents (public)
- `GET /api/v1/profile/` — User profile
- `GET /api/v1/leaderboard/` — Leaderboard with display_name, streak_days (public)
- `GET /api/v1/achievements/` — User achievements with progress (current/target per achievement)
- `GET /api/v1/analytics/` — Analytics dashboard (overview, xp distribution, popular lessons, path progress, activity 7d, achievements summary, chat stats)
- `GET /api/v1/email-preview/<template>/` — Preview email templates (DEBUG only)
- `POST /api/v1/auth/login/` — Login
- `GET /api/v1/auth/demo-users/` — Demo users (public)

### Serializers (notable additions)
- **LeaderboardSerializer**: includes `display_name` (first+last name or username) and `streak_days`
- **AchievementWithUnlockSerializer**: includes `progress` field `{current, target}` per achievement
- **LessonWithProgressSerializer**: includes `completed` boolean and `completed_at` per lesson
- **LearningPathListSerializer**: includes nested `lessons` with completion status, `total_xp`

### Certificate System
- `core/certificates.py`: `generate_certificate()` — landscape A4 PDF with dark theme, German text, cert ID
- `lessons/views.py`: `CertificateView` — validates all lessons completed, returns PDF with Content-Disposition

### Email System
- `core/emails.py`: 5 email types with HTML dark-theme templates + plaintext fallbacks
  - `send_welcome_email` — registration
  - `send_achievement_email` — achievement unlock
  - `send_level_up_email` — level up (titles: Anfaenger→Grossmeister)
  - `send_path_completed_email` — path completion with certificate link
  - `send_streak_reminder_email` — streak at risk
- `_should_send()` checks email + `email_notifications` preference
- `get_preview_html()` for browser-viewable previews
- Integration in `LessonCompleteView`: level-up, achievement, path-complete emails triggered automatically
- Console backend in dev, SMTP-ready for production

### Seed Data
- 4 learning paths: AI Grundlagen (4), Prompt Engineering (3), Agentic Workflows (5), AI in Finance (5)
- 5 achievements: first-lesson, first-chat, three-streak, all-basics, xp-100
- 2 chat agents: general (AI Tutor), finance (Finance AI)
- 3 demo users: demo (Gina M.), anna (Anna M., xp=520), marco (Marco L., xp=410)

### Tests — 471 passing
- core: 233 (UserProfile, Achievement, UserAchievement, API, Leaderboard display_name, Achievement progress, Analytics 72, Email 75)
- lessons: 140 (LearningPath, Lesson, LessonProgress, API, PathListLessonsField, Certificate 37)
- chat: 84 (ChatMessage 18, ChatAPI 17, ChatAchievement 7, ChatAgent model 13, Agents API 9, Chat with Agent 11, + management cmd tests)

## Frontend Structure
- `frontend/` — React 19 + Vite + TypeScript
- MUI v5 Dark Theme with custom palette
- Framer Motion animations on all pages (fade+slideUp, stagger)
- DashboardLayout: collapsible sidebar with active indicator
- Routes: `/` `/learn` `/learn/:pathSlug` `/learn/:pathSlug/:lessonSlug` `/leaderboard` `/analytics` `/profile` `/achievements` `/chat`

### Pages (all connected to real API)
- **DashboardPage**: StatCards from API, learning paths with progress (navigate to path detail), leaderboard top 5, "Next Mission" card — Skeleton loading
- **LeaderboardPage**: Full table with Top-3 medals, own row highlighted, Level chips, animated XP CountUp, streak display
- **AchievementsPage**: Grid with unlocked (glow, date) / locked (grayscale, progress bar) states, stats header
- **ProfilePage**: 2-column layout — avatar + info, XP bar + streak calendar (30-day grid) + recent achievements + learning progress
- **LearningPathsPage**: Collapsible PathCards with timeline lessons, pulse animation for current lesson, auto-expand first active path
- **LearningPathDetailPage**: Hero header with gradient, breadcrumbs, difficulty/XP chips, progress bar, timeline with lesson cards, "Weiterlernen" button
- **LessonPage**: Markdown content + ChatPanel, breadcrumbs (Lernpfade > Path > Lesson), path progress bar, completion button, "Nächste Lektion" button after completing
- **AnalyticsPage**: Recharts dashboard — AreaChart, BarChart, PieChart, path progress bars, achievement highlights, 6 mini stat cards with CountUp
- **ChatPage**: Agent selection via Chips, ChatPanel with agentSlug
- **LoginPage**: Demo user tiles with one-click login, manual login expandable

## Next Steps
- Frontend: Certificate download button on LearningPathDetailPage (100% completed paths)
- Frontend: Certificate celebration on LessonPage when completing last lesson of a path
- Frontend: Email notification toggle on ProfilePage
- Add more specialized agents (e.g., Code AI, Ethics AI)
- Code splitting for bundle size optimization
- Real daily activity tracking for streak calendar
