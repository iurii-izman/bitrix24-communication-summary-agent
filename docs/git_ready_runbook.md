# Git-Ready Runbook

## Goal

Initialize and publish the project without leaking local state, secrets, or validation leftovers.

## Preflight

- Confirm `.env` is present locally and remains untracked.
- Confirm `runtime_artifacts/` contains no files you plan to publish.
- Confirm `demo.sqlite3` and any other local `.sqlite3` files stay ignored.

## Initialize Repository

PowerShell:

```powershell
git init
git add .
git status --short
```

Review the staged set before the first commit. Expected exclusions:
- `.env`
- `runtime_artifacts/`
- `*.sqlite3`
- `.venv/`
- caches and coverage output

## First Commit

```powershell
git commit -m "feat: finalize Bitrix24 communication summary agent MVP"
```

## Optional Tag

```powershell
git tag -a v0.1.0 -m "v0.1.0 - portfolio-ready FastAPI MVP with validated Bitrix24 live test workflow and cleanup audit"
```

## Final Verification

Run before push:

```powershell
pytest -q
ruff check .
```

Spot-check:
- [README.md](C:\dev_bitrix24\bitrix24-communication-summary-agent\README.md)
- [docs/publication_pack.md](C:\dev_bitrix24\bitrix24-communication-summary-agent\docs\publication_pack.md)
- [docs/screenshots_plan.md](C:\dev_bitrix24\bitrix24-communication-summary-agent\docs\screenshots_plan.md)
- [SECURITY.md](C:\dev_bitrix24\bitrix24-communication-summary-agent\SECURITY.md)

## Push Checklist

- Choose public or private visibility intentionally.
- Add repository description and topics from `docs/publication_pack.md`.
- Add screenshots only after the safety review from `docs/screenshots_capture_checklist.md`.
- If you mention live Bitrix24 validation publicly, mention that it was done on a test portal with scripted cleanup.
