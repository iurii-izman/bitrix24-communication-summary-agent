# CRM Communication Summary Agent

Public-safe disclaimer: demo/product prototype. Not a commercial deployment.

One-line summary:
AI communication processing layer for Bitrix24 that turns messy client communication into structured CRM action with human approval before critical sync.

Problem:
Client calls, emails, chat snippets, and manager notes often stay unstructured, which slows follow-up and creates CRM hygiene gaps.

Solution:
Accept communication text through a protected API, summarize it, extract agreements and risks, route uncertain cases into review, and prepare Bitrix24 timeline/task actions in dry-run-safe mode.

What was built:
- FastAPI backend
- SQLite-backed queue and logs
- deterministic mock AI provider + fallback
- routing gate and review path
- Bitrix24 mock and real-ready adapter boundary
- Basic Auth admin UI

Architecture:
`source -> intake API -> DB queue -> worker -> AI -> routing -> review or Bitrix action`

Confirmed baseline:
- local demo mode
- tests and lint
- smoke script
- real Bitrix24 test-portal validation on July 7, 2026
- live timeline comment and live task creation confirmed
- batch live validation confirmed
- cleanup and cleanup audit confirmed against saved validation artifacts

Why this is a strong portfolio case:
- CRM domain relevance
- AI safety-first workflow
- integration boundary design
- explicit state machine and dry-run logic
- public-safe packaging

Trade-offs:
- SQLite and in-process worker keep the MVP simple
- OpenAI path is optional and not required for runtime
- real Bitrix writes are blocked by default outside controlled validation runs

Suggested visuals:
- dashboard
- review queue
- communication detail with summary
- live validation artifact with real IDs
- cleanup audit proof
- green test run

CV wording:

CRM Communication Summary Agent  
AI-прототип для обработки коммуникаций по сделкам в Bitrix24: summary звонков, писем и заметок, извлечение договорённостей, рисков и next steps, генерация follow-up задач и комментариев в timeline CRM. Стек: Python, FastAPI, Pydantic, SQLite, Bitrix24 REST API, mock/OpenAI provider boundary, human-in-the-loop, dry-run/live mode.

CRM Communication Summary Agent  
A demo/product prototype for Bitrix24 communication processing: turns calls, emails, chats, and manager notes into structured summaries, agreements, risks, next steps, follow-up tasks, draft replies, and CRM timeline comments using a human-in-the-loop workflow.
