# Bitrix24 Communication Summary Agent

![CI](https://github.com/iurii-izman/bitrix24-communication-summary-agent/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-0F766E.svg)
![Last Commit](https://img.shields.io/github/last-commit/iurii-izman/bitrix24-communication-summary-agent)
![Issues](https://img.shields.io/github/issues/iurii-izman/bitrix24-communication-summary-agent)
![Docs](https://img.shields.io/badge/docs-architecture%20%2B%20runbooks-2563EB.svg)
![Status](https://img.shields.io/badge/status-demo%2Fproduct%20prototype-1F6FEB.svg)
![Bitrix24](https://img.shields.io/badge/Bitrix24-mock%2Freal--ready-0EA5E9.svg)
![Community](https://img.shields.io/badge/community-templates%20enabled-F59E0B.svg)

> Demo/product prototype. Not a commercial deployment.

Bitrix24 Communication Summary Agent is a portfolio-ready MVP for processing calls, emails, chats, and manager notes into structured CRM actions: summary, agreements, risks, missing info, next steps, follow-up tasks, draft replies, and Bitrix24 timeline comments with human-in-the-loop approval.

## Highlights

- FastAPI backend with protected intake API and masked admin UI.
- Deterministic AI-summary flow with review routing and operator override path.
- Mock-first runtime plus validated real Bitrix24 test-portal workflow.
- Cleanup and audit scripts for safe live experimentation on test artifacts.
- Public-repo scaffolding: CI, security policy, support guidance, issue forms, and release docs.

## Why this repo is worth reviewing

- Clear CRM automation scenario with explicit AI and Bitrix24 boundaries.
- Demo-safe local runtime with SQLite, mock AI, and mock Bitrix24 by default.
- Human-in-the-loop workflow with review queue and admin actions.
- Tests, linting, docs, Docker, and public-safe masking included.

## Repository Health

- [License](./LICENSE)
- [Code of Conduct](./CODE_OF_CONDUCT.md)
- [Contributing](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)
- [Support](./SUPPORT.md)
- [CI Workflow](./.github/workflows/ci.yml)
- [Dependabot](./.github/dependabot.yml)

## Architecture Flow

`Communication source -> Protected API -> SQLite queue -> Worker -> AI summary -> Routing gate -> Review or Bitrix sync -> Logs`

## Quick Start

PowerShell:

```powershell
copy .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Docker:

```powershell
copy .env.example .env
docker compose up --build
```

Run checks:

```powershell
pytest -q
ruff check .
python scripts\smoke_test.py
```

Live validation:

```powershell
python scripts\live_bitrix_validation.py --deal-id 1 --enable-write
python scripts\batch_live_validation.py --deal-ids 1,2 --enable-write
python scripts\cleanup_live_artifacts.py --artifact .\runtime_artifacts\bitrix_validation\<artifact>.json
python scripts\cleanup_live_artifacts.py --artifact .\runtime_artifacts\bitrix_validation\<artifact>.json --execute
```

## Demo Mode

Default demo-safe settings:
- `APP_MODE=demo`
- `AI_PROVIDER=mock`
- `BITRIX_MODE=mock`
- `ALLOW_BITRIX_WRITE=false`
- `MASKING_ENABLED=true`

## Real Mode Boundaries

- `AI_PROVIDER=openai` is implemented as an optional boundary only.
- `BITRIX_MODE=real` uses a real adapter boundary with dry-run guard.
- Real writes stay blocked unless `ALLOW_BITRIX_WRITE=true`.

Validated real Bitrix24 baseline as of July 7, 2026:
- real webhook boundary exercised against a test portal
- `tasks.task.add` validated with live writes
- `crm.timeline.comment.add` validated with live writes
- safe dry-run and live-write paths both exercised

Controlled validation command:

```powershell
python scripts\live_bitrix_validation.py --deal-id 1 --enable-write
```

## API

- `GET /health`
- `POST /api/v1/communications`
- `GET /api/v1/communications/{request_id}`

Public API requires `X-Webhook-Secret`.

## Admin UI

- `/` dashboard
- `/admin/communications`
- `/admin/communications/{request_id}`
- `/admin/review`
- `/admin/settings`

Admin UI uses Basic Auth from `.env`.

## Security

- No `.env` in git.
- Synthetic demo data only.
- Basic Auth for admin UI.
- Webhook secret for public API.
- No automatic client messaging.
- Settings and errors are masked.
- `.dockerignore` excludes local credentials and validation artifacts from container builds.

Additional reference:
- [Security policy](./SECURITY.md)
- [Contribution guide](./CONTRIBUTING.md)

## Portfolio Assets

- [Architecture](./docs/architecture.md)
- [ADR decisions](./docs/adr/)
- [Bitrix cleanup runbook](./docs/bitrix_cleanup_runbook.md)
- [Project status](./docs/project_status.md)
- [Notion case](./docs/notion_case.md)
- [Publication pack](./docs/publication_pack.md)
- [Final release pack](./docs/final_release_pack.md)
- [Git-ready runbook](./docs/git_ready_runbook.md)
- [Repository description variants](./docs/repo_description.md)
- [Demo walkthrough](./docs/demo_walkthrough.md)
- [Screenshot capture checklist](./docs/screenshots_capture_checklist.md)
- [Release note](./docs/release_note.md)
- [Release checklist](./docs/checklists/release_checklist.md)
- [GitHub repo launch guide](./docs/github_repo_launch.md)

## Production Upgrade Path

Natural next upgrades: PostgreSQL, migrations, external worker, stronger auth, richer audit logging, and portal-specific Bitrix field mapping.

## Current Known Boundaries

- OpenAI path exists but is not required for tests and is not validated in this repository by default.
- The repository stays positioned as a demo/product prototype even though the Bitrix24 test-portal path was validated.
- Cleanup of live validation artifacts is manual-by-script, not automatic.

## CV-ready block

CRM Communication Summary Agent  
AI-прототип для обработки коммуникаций по сделкам в Bitrix24: summary звонков, писем и заметок, извлечение договорённостей, рисков и next steps, генерация follow-up задач и комментариев в timeline CRM. Стек: Python, FastAPI, Pydantic, SQLite, Bitrix24 REST API, mock/OpenAI provider boundary, human-in-the-loop, dry-run/live mode.

CRM Communication Summary Agent  
A demo/product prototype for Bitrix24 communication processing: turns calls, emails, chats, and manager notes into structured summaries, agreements, risks, next steps, follow-up tasks, draft replies, and CRM timeline comments using a human-in-the-loop workflow.

Do not commit secrets. Use `.env.example` as the baseline and keep local credentials out of version control.
