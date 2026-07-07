# ADR 003 — Worker Strategy

## Status
Accepted

## Context

The first delivery needs asynchronous processing without adding external infrastructure that would complicate local setup and demos.

## Decision

- Use a DB queue plus an in-process worker for the MVP.
- Do not use Celery, Redis, or an external queue in the MVP.
- Keep the orchestration replaceable later.

## Consequences

- Low operational overhead for local validation.
- Easy to demo the end-to-end pipeline.
- Future migration to external workers remains possible.

## Alternatives Considered

- Celery with Redis.
- Managed queue services from the start.
