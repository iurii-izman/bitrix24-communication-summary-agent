# ADR 002 — Bitrix24 Integration Mode

## Status
Accepted

## Context

Bitrix24 portals differ, and this repository must support both demo-safe behavior and controlled real portal validation.

## Decision

- `BITRIX_MODE=mock|real`
- `ALLOW_BITRIX_WRITE=false|true`
- mock adapter is the default demo path
- real adapter uses webhook-based REST calls
- timeline comments use `crm.timeline.comment.add`
- tasks use `tasks.task.add`
- cleanup and cleanup-audit scripts operate on saved validation artifacts

## Consequences

- The same app can demo safely or validate against a test portal.
- Live validation remains explicit and auditable.
- Cleanup is reproducible instead of ad hoc.

## Alternatives Considered

- Hardcoding a single live-only portal path.
- Removing real mode from the repository entirely.
