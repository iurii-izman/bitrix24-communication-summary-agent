# Final Release Pack

## Recommended Version

`v0.1.0`

## Suggested Commit Title

`feat: finalize Bitrix24 communication summary agent MVP`

## Suggested Tag Annotation

`v0.1.0 - portfolio-ready FastAPI MVP with validated Bitrix24 live test workflow and cleanup audit`

## Release Summary

Bitrix24 Communication Summary Agent is a demo/product prototype that accepts calls, emails, chats, and manager notes, turns them into structured summaries and follow-up actions, and routes uncertain cases into human review before CRM writeback.

This release includes:
- protected FastAPI intake API and admin UI
- deterministic summary pipeline with review routing
- mock and real Bitrix24 integration boundaries
- live validation scripts for timeline comments and tasks
- cleanup and cleanup-audit scripts for safe test-portal experimentation
- tests, linting, Docker, ADRs, security notes, and publication assets

## Publish Order

1. Initialize git and commit the current tree.
2. Verify `.env` is excluded and `runtime_artifacts/` is clean.
3. Run `pytest -q` and `ruff check .`.
4. Capture the screenshot set from `docs/screenshots_plan.md`.
5. Copy the repository description from `docs/repo_description.md`.
6. Copy the public positioning text from `docs/publication_pack.md`.
7. Create tag `v0.1.0`.

## GitHub Release Body

```markdown
## Bitrix24 Communication Summary Agent v0.1.0

Portfolio-ready FastAPI MVP for Bitrix24 communication processing.

### Included
- protected communication intake API
- review queue and masked admin dashboard
- structured summary, risk, and next-step extraction
- Bitrix24 timeline comment and task writeback boundary
- live validation, batch validation, cleanup, and cleanup audit scripts
- tests, linting, Docker, and publication docs

### Validated
- demo-safe local runtime
- real Bitrix24 test-portal write path
- repeated batch validation scenarios
- cleanup of created portal artifacts

### Notes
- positioned as a demo/product prototype, not a production deployment
- secrets and portal-specific credentials are intentionally excluded
```

## Final Sanity Check

- README matches the current UI and capabilities.
- All screenshots use masked or synthetic data.
- No artifact JSON or local databases are staged for publish.
- The repository description and release note use the same positioning language.
