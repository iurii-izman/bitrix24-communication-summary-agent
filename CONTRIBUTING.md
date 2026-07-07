# Contributing

## Project Posture

This repository is a demo/product prototype with production-capable seams.

Before changing anything:
- read [docs/project_status.md](./docs/project_status.md)
- read [docs/architecture.md](./docs/architecture.md)
- read the relevant checklist or runbook for the area you are touching

## Working Style

- Prefer small, auditable changes.
- Keep route handlers thin.
- Keep business logic in services and Bitrix/AI boundaries.
- Do not rebuild implemented layers from scratch when a focused extension is enough.
- Preserve the standalone project posture; this is not a feature branch of another repo.

## Safety Rules

- Never commit secrets.
- Never commit real PII.
- Keep demo data synthetic.
- Preserve masking in UI, docs, logs, and screenshots.
- Keep `ALLOW_BITRIX_WRITE=false` outside controlled validation runs.

## Verification

Run before proposing merge:

```bash
pytest -q
ruff check .
```

If the work affects live validation or portal hygiene, also run the relevant script:

```bash
python scripts/live_bitrix_validation.py --deal-id 1
python scripts/cleanup_live_artifacts.py --artifact <artifact_path>
python scripts/cleanup_audit.py --artifact <artifact_path>
```

## Pull Requests

- Keep scope aligned with one concrete feature or maintenance task.
- Update docs when behavior, scope, or repo posture changes.
- Do not claim production rollout or commercial deployment.
