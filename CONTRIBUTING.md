# Contributing Guide

## Branch Strategy
- `main`: stable branch, always releasable.
- Feature work: create short-lived branches from `main`, for example `feat/index-stat-cache`.
- Use pull requests for all changes. Do not push directly to `main`.

## Commit Messages
Use Conventional Commits:
- `feat: ...`
- `fix: ...`
- `refactor: ...`
- `test: ...`
- `docs: ...`

Example:
`feat(stats): add monthly return aggregation endpoint`

## Recommended Local Workflow
1. Sync latest code: `git pull origin main`
2. Create branch: `git checkout -b feat/your-change`
3. Make changes and run checks:
   - `pytest backend/tests -q`
   - `cd frontend && npm run build`
4. Commit with clear scope:
   - `git add .`
   - `git commit -m "feat(api): add index comparison endpoint"`
5. Push branch and open a pull request.

## Pull Request Checklist
- Include a clear summary of behavior changes.
- List impacted paths (for example `backend/app/api/stats.py`).
- Include test evidence (commands + results).
- Attach screenshots for frontend view changes.

## Large Files and Secrets
- Do not commit secrets (`.env`, keys, tokens).
- Do not commit generated data or logs.
- Keep database/runtime artifacts out of version control.

