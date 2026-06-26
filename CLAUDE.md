# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

MBA skills challenge (`desafio-skills`). Contains three intentionally flawed legacy projects used as input for the `/refactor-arch` skill, plus generated audit reports.

## Projects

| Project | Stack | Port | Start |
|---------|-------|------|-------|
| `code-smells-project/` | Python/Flask + SQLite | 5000 | `pip install -r requirements.txt && python app.py` |
| `task-manager-api/` | Python/Flask + SQLAlchemy + SQLite | 5000 | `pip install -r requirements.txt && python seed.py && python app.py` |
| `ecommerce-api-legacy/` | Node.js/Express + SQLite (in-memory) | 3000 | `npm install && npm start` |

**task-manager-api**: run `seed.py` before first boot or endpoints return empty data.

**ecommerce-api-legacy**: SQLite is in-memory — data resets on each restart. Request examples in `api.http`.

## Architecture

### code-smells-project (already refactored to MVC)
- Entry: `app.py` (composition root, Flask factory)
- `src/config/settings.py` — env-based config
- `src/models/` — raw SQLite via `database.py` (module-level connection)
- `src/controllers/` — business logic
- `src/views/` — Blueprint route definitions (thin HTTP layer)
- `src/middlewares/error_handler.py` — centralized error handling
- Original monolithic files (`controllers.py`, `models.py`) left at root for reference

### task-manager-api (already refactored to MVC)
- Entry: `app.py`
- `config/settings.py` — env-based config
- `database.py` — SQLAlchemy instance (`db = SQLAlchemy()`)
- `models/` — SQLAlchemy ORM models
- `controllers/` — business logic
- `routes/` — Blueprint route definitions
- `services/notification_service.py` — notification abstraction
- `middlewares/error_handler.py`
- Run `seed.py` separately before first boot

### ecommerce-api-legacy (already refactored from God Class)
- Entry: `src/app.js` (Express composition root)
- `src/config/settings.js` — env-based config
- `src/models/` — per-entity SQLite access (db.js, userModel.js, courseModel.js, enrollmentModel.js, auditModel.js)
- `src/controllers/` — checkoutController, reportController, userController
- `src/routes/` — thin Express routers
- `src/middlewares/errorHandler.js`
- Original monolithic `src/AppManager.js` and `src/utils.js` left for reference

## Skill: `/refactor-arch`

The `refactor-arch` skill lives at two locations:
- Root: `.claude/skills/refactor-arch/` (global, used for any project)
- `code-smells-project/.claude/skills/refactor-arch/` (project-local copy)

Skill reference files (load order matters — SKILL.md enforces it):
1. `project-analysis.md`
2. `anti-patterns-catalog.md` *(not yet in repo — skill reads it from catalog)*
3. `audit-report-template.md`
4. `mvc-guidelines.md`
5. `refactoring-playbook.md`

Skill has 3 phases: Analysis → Audit (read-only, pauses for confirmation) → Refactoring.

## Audit Reports

Generated reports land in `reports/`:
- `audit-project-1.md` — code-smells-project (22 findings: 7 CRITICAL / 4 HIGH / 5 MEDIUM / 6 LOW)
- `audit-project-2.md` — ecommerce-api-legacy (19 findings: 4 CRITICAL / 4 HIGH / 5 MEDIUM / 6 LOW)
