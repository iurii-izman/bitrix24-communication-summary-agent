# Screenshots Capture Checklist

## Goal

Capture a coherent, public-safe visual set from the actual implemented UI and validated demo flow.

Use this checklist together with:
- [docs/screenshots_plan.md](./screenshots_plan.md)
- [docs/demo_walkthrough.md](./demo_walkthrough.md)

## Before Capture

- Start the app in demo-safe mode or a controlled real-mode screen you are prepared to show.
- Use only synthetic communications.
- Prepare at least one request in each useful state:
  - completed
  - review_needed
  - dropped if relevant
  - failed or failed_retryable if relevant
- Close unrelated apps and tabs.

## Required Safety Checks

- No `.env` contents visible anywhere.
- No real email, phone, name, or company data visible.
- No webhook token fragments visible.
- No raw Bitrix webhook URLs visible.
- No local filesystem paths shown unless intentionally part of a developer-facing screenshot.
- No browser bookmarks, chat messages, or desktop notifications visible.

## Recommended Capture Set

1. `01_dashboard_control_room.png`
   Show summary cards, channel mix, and recent records.

2. `03_review_needed_detail.png`
   Show missing info, risks, and human approval actions.

3. `04_completed_detail.png`
   Show timeline comment preview and processing logs.

4. `02_communications_queue.png`
   Show queue density and masked identifiers.

5. `05_live_validation_artifact.png`
   Show saved validation evidence with task and comment IDs.

6. `07_cleanup_audit.png`
   Show that test-portal artifacts were removed successfully.

7. `08_green_checks.png`
   Show `pytest -q` and `ruff check .`.

## Optional Capture Set

1. `09_runtime_health.png`
   Show Docker startup or `/health`.

2. `admin_settings_snapshot.png`
   Show masked runtime values only.

## Composition Guidance

- Prefer consistent browser zoom and window size.
- Keep one visual style across the whole set.
- Crop aggressively; remove dead space and irrelevant chrome.
- If the address bar reveals anything you do not want to publish, crop it out.

## Final Review Before Publication

- Every visible personal field is synthetic or masked.
- The screenshots match the current UI, not an outdated layout.
- The visual sequence tells the same story as the README and Notion case.
- The filenames match `docs/screenshots_plan.md` so they can be reused in README, Notion, or release notes without renaming.
