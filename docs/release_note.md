# Release Note v0.1.0

Included:
- FastAPI backend
- protected intake API
- SQLite queue and logs
- deterministic AI summary flow
- review queue and admin actions
- Bitrix24 mock and real-ready boundaries
- tests, ruff, Docker, docs

Validated:
- local demo mode
- smoke script
- lint and tests
- Docker startup
- real Bitrix24 test-portal write path for timeline comments and tasks
- batch live validation across repeated scenarios
- cleanup script and cleanup audit against saved validation artifacts

Known boundaries:
- no audio transcription
- no RAG
- no external queue
- OpenAI path optional only
