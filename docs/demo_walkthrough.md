# Demo Walkthrough

1. Copy `.env.example` to `.env`.
2. Start the app with `uvicorn app.main:app --reload`.
3. Seed demo data with `python scripts\seed_demo_data.py`.
4. Submit a sample communication to `POST /api/v1/communications`.
5. Open `/` and sign in with Basic Auth.
6. Inspect `/admin/review` for review-needed cases.
7. Open a record detail and use approve/retry/drop/reprocess.
8. Show the mock Bitrix planned action in processing logs.
9. For the test portal, run `python scripts\live_bitrix_validation.py --deal-id 1 --enable-write`.
10. Capture the printed artifact path and use `python scripts\cleanup_live_artifacts.py --artifact <artifact_path> --execute`.
