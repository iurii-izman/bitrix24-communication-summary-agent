# Security Policy

## Repository Scope

This repository is a public-safe demo/product prototype.

It must not contain:
- secrets
- production credentials
- real customer data
- unmasked screenshots with personal data

## Expected Safeguards

- `.env` is ignored
- `.dockerignore` excludes secrets, caches, virtualenvs, and local validation artifacts
- demo data is synthetic
- intake payloads are masked for storage and presentation
- admin UI is protected with Basic Auth
- intake API is protected with `X-Webhook-Secret`
- tests do not require real external network calls
- real Bitrix24 writes are blocked by default unless explicitly enabled for controlled validation

## Test-Portal Validation Rules

- use only synthetic communications
- keep `ALLOW_BITRIX_WRITE=false` outside controlled validation runs
- save live validation artifacts under local `runtime_artifacts/`
- remove test timeline comments and tasks with the cleanup scripts after validation
- verify cleanup with `python scripts\cleanup_audit.py --artifact <artifact_path>`

## Reporting

If you find a security issue in the repository:
- do not publish secrets or sensitive payloads in a public issue
- redact all PII and credentials
- provide reproduction steps with synthetic data when possible

## Notes

This repository is not positioned as a live commercial deployment. Security hardening for an internal-production rollout would require stronger auth, secret management, audit controls, database migrations, and deployment posture beyond the current portfolio baseline.
