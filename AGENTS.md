# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service and data refresh pipeline.
- `backend/app/api/`: HTTP endpoints (`indices`, `stats`, `tasks`).
- `backend/app/services/`: analytics and data access logic.
- `backend/app/models/`, `backend/app/core/`, `backend/app/tasks/`: ORM entities, shared config/database code, scheduled jobs.
- `backend/tests/`: backend unit tests (`pytest`).
- `frontend/`: Vue 3 + Vite TypeScript UI (`src/views`, `src/router`, `src/api`).
- Root scripts like `main.py`, `index_analyzer_v2.py`, and `process_index_data.py` support legacy/offline report generation.
- Runtime artifacts: `backend/data/summarize_etf.db`, `backend/logs/`, and `output/`.

## Build, Test, and Development Commands
- Install Python deps: `pip install -r requirements.txt`
- Refresh ETF/index data: `python backend/scripts/refresh_data.py`
- Start API (dev): `uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000`
- Run backend tests: `pytest backend/tests -q`
- Frontend setup: `cd frontend && npm install`
- Frontend dev server: `cd frontend && npm run dev`
- Frontend production build: `cd frontend && npm run build`
- Frontend preview build: `cd frontend && npm run preview`

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints where practical, `snake_case` for functions/modules, `PascalCase` for classes.
- TypeScript/Vue: follow existing style (double quotes, semicolons, composition-friendly modules), `PascalCase` for view components (for example `IndexDetailView.vue`).
- Keep API routes grouped by domain under `backend/app/api/`; keep reusable logic out of route handlers.
- No repo-level formatter/linter config is currently checked in; keep changes minimal, consistent, and readable.

## Testing Guidelines
- Framework: `pytest` (backend only in current tree).
- Place tests under `backend/tests/` and name files `test_*.py`.
- Prefer small unit tests for service logic (example: `backend/tests/test_analytics.py`).
- Run tests locally before opening a PR: `pytest backend/tests -q`.

## Commit & Pull Request Guidelines
- Git history is not available in this workspace snapshot (`.git` missing), so follow Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`.
- Keep commits focused and atomic; include data/schema updates in the same PR when tightly coupled.
- PRs should include:
  - clear summary of behavior changes,
  - impacted paths (for example `backend/app/api/stats.py`),
  - test evidence (command + result),
  - UI screenshots for frontend view changes.
