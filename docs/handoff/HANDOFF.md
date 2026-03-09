# Handoff — AI Learning Hub

## Current State
- Project initialized with basic repo structure
- Claude Code configuration added (CLAUDE.md, skills, commands)
- Django backend project structure created and verified
- React + Vite frontend created with MUI Dark Theme, routing, and layout

## Backend Structure
- `backend/` — Django project `ai_learning_hub`
- Apps: `core` (User/Profile/XP), `lessons` (Lernpfade), `chat` (AI-Tutor)
- Packages: Django 6.0, DRF, django-cors-headers, anthropic, python-dotenv, pytest, ruff
- Config: CORS enabled, DRF with Basic+Session auth, SQLite, dotenv loaded
- `backend/pytest.ini` — pytest configured with DJANGO_SETTINGS_MODULE
- `backend/requirements.txt` — frozen dependencies

## Last Commit
- `8415f48` — `chore(claude): add Claude Code project configuration`
- Added: CLAUDE.md, .claude/ (commands, skills, settings), .agents/skills/, skills-lock.json

## Frontend Structure
- `frontend/` — React 18 + Vite + TypeScript
- MUI v5 Dark Theme with custom palette (see `docs/knowledge/design.md`)
- DashboardLayout: collapsible sidebar (280px/72px) + topbar + main content
- Routes: `/` Dashboard, `/learn` Lernpfade, `/learn/:id` Lektion, `/leaderboard`, `/profile`, `/achievements`
- Packages: MUI, react-router-dom, axios, framer-motion, recharts

## Next Steps
- Define initial data models
- Create first API endpoints
- Connect frontend to backend API
