# Commit, Push und Scratchpad aktualisieren

## Ablauf
1. `git status --porcelain` — wenn leer, abbrechen mit "Nothing to commit"
2. `git add -A`
3. Commit Message nach Conventional Commits formulieren (feat/fix/refactor/chore/docs)
4. `git push origin main`
5. Update docs/handoff/HANDOFF.md mit dem was committed wurde

## Commit Message Format
- feat(scope): description — neues Feature
- fix(scope): description — Bugfix
- refactor(scope): description — Code-Umbau ohne Verhaltensänderung
- chore(scope): description — Tooling, Config, Dependencies
- docs(scope): description — Nur Dokumentation
