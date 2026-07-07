# Screenshots Plan

## Core Product Story

1. `01_dashboard_control_room.png`
   Show queue counters, risk/priority cards, and settings snapshot.

2. `02_communications_queue.png`
   Show mixed statuses and masked client info.

3. `03_review_needed_detail.png`
   Show summary, missing info, risks, and approval actions.

4. `04_completed_detail.png`
   Show timeline comment preview, draft reply, and processing logs.

## Validation Story

5. `05_live_validation_artifact.png`
   Show real timeline comment ID and task ID from a saved artifact.

6. `06_cleanup_preview.png`
   Show cleanup dry-run output against the same artifact.

7. `07_cleanup_audit.png`
   Show audit summary proving created items were removed.

## Engineering Proof

8. `08_green_checks.png`
   Show `pytest -q` and `ruff check .`.

9. `09_runtime_health.png`
   Show Docker startup or `/health` response if useful.

## Publishing Order

- Lead with `01_dashboard_control_room.png`.
- Use `03_review_needed_detail.png` as the strongest workflow proof.
- Keep validation images after product UI so the repo story stays product-first.
- Put `08_green_checks.png` and `09_runtime_health.png` last as engineering evidence.

## Capture Notes

- Crop browser chrome aggressively.
- Keep the same zoom and browser width across UI screenshots.
- Prefer the new dashboard hero section as the first visual.
- Do not show raw portal URLs, secrets, or local filesystem paths unless intentionally presenting developer workflow.
