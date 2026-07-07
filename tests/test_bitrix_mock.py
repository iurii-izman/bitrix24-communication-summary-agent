from app.services.bitrix_mock import MockBitrixAdapter


def test_add_timeline_comment_mock_works() -> None:
    adapter = MockBitrixAdapter()
    result = adapter.add_timeline_comment("123", "Comment")
    assert result["ok"] is True
    assert result["dry_run"] is True


def test_create_task_mock_works() -> None:
    adapter = MockBitrixAdapter()
    result = adapter.create_task("123", "Task", "Desc", "2026-07-08", 1)
    assert result["ok"] is True
    assert result["planned_action"]["title"] == "Task"


def test_dry_run_behavior_works() -> None:
    adapter = MockBitrixAdapter(allow_write=False)
    result = adapter.create_task("123", "Task", "Desc", "2026-07-08", 1)
    assert result["dry_run"] is True
