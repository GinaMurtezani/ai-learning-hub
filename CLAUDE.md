# AI Learning Hub — Claude Code Configuration

## Project
AI Learning Hub — eine spielerische Lernplattform für AI-Kompetenzen.
Tech Stack: Python 3.12, Django 5.x, Django REST Framework, React 18, TypeScript, MUI v5 (Dark Theme), SQLite, Anthropic API.

## Architecture
- backend/ — Django Project (ai_learning_hub)
- frontend/ — React + Vite + TypeScript + MUI

## Workflow Rules
1. Describe approach and wait for approval before coding
2. If >3 files affected, break into smaller rounds
3. After coding, list what could break + suggest tests
4. Bug = write failing test first, then fix
5. Run tests after every change: cd backend && .venv\Scripts\python.exe -m pytest -q

## Session Start
- Read docs/handoff/HANDOFF.md for current state
- Read docs/knowledge/ files for domain context

## Verification Commands
- Backend tests: cd backend && .venv\Scripts\python.exe -m pytest -q
- Frontend types: cd frontend && npx tsc --noEmit
- Frontend lint: cd frontend && npx eslint src/ --quiet
- Backend lint: cd backend && .venv\Scripts\python.exe -m ruff check .

## Testing Philosophy (CRITICAL — NON-NEGOTIABLE)
- **Test flooding:** Every feature gets MASSIVE test coverage. Not 2-3 tests, aim for 10-20+ per feature.
- Test every happy path, every edge case, every error case, every boundary value.
- New model? Test creation, validation, constraints, __str__, relationships, defaults, nullability.
- New endpoint? Test success, auth failure, validation errors, empty data, pagination, filtering, edge cases.
- New calculation? Test all input ranges, boundary values, zero, negative, very large numbers, rounding.
- **Test Integrity:** Existing test fails after code change = CODE is wrong, not the test
- NEVER modify existing test assertions to make tests pass
- New behavior = new test, not modified existing test
- When in doubt: write MORE tests. Over-testing is not a thing in this project.

## Platform (Windows)
- Python: .venv\Scripts\python.exe (backslash, not forward slash)
- PowerShell: Use ; not && for command chaining
- nul is reserved — never use as filename or redirect target

## Doc-Consistency Rule
When changing code behavior, check if these need updates:
- CLAUDE.md, docs/knowledge/*.md, docs/handoff/HANDOFF.md
