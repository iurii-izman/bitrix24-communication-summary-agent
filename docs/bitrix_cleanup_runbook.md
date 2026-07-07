# Bitrix24 Cleanup Runbook

Use this runbook after live validation on the test portal.

Sources:
- `tasks.task.delete` uses `taskId` as documented by Bitrix24 REST API.
- `crm.timeline.comment.delete` uses `id`, `ownerTypeId`, and `ownerId`; for deals, `ownerTypeId=2`.

Recommended flow:
1. Run live validation and keep the artifact path printed by the script.
2. Preview cleanup:
   `python scripts\cleanup_live_artifacts.py --artifact <artifact_path>`
3. Execute cleanup:
   `python scripts\cleanup_live_artifacts.py --artifact <artifact_path> --execute`
4. Re-open the deal card in Bitrix24 and confirm that the test comment and task were removed.

Notes:
- The cleanup script deletes only IDs recorded in the artifact.
- Review-only scenarios do not create Bitrix items, so they are printed with null IDs and skipped.
- Keep `ALLOW_BITRIX_WRITE=false` in `.env` after validation. The cleanup script calls Bitrix24 directly and does not depend on app write mode.
