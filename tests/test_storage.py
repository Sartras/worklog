from datetime import datetime, timezone
from pathlib import Path

import pytest

from worklog.models import Session
from worklog.storage import StorageError, active_session, load_sessions, save_sessions


def test_save_and_load_sessions_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "worklog.json"
    started_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    sessions = [Session(task_id=2, title="Example", started_at=started_at)]

    save_sessions(path, sessions)
    loaded = load_sessions(path)

    assert loaded == sessions


def test_load_sessions_returns_empty_for_missing_file(tmp_path: Path) -> None:
    assert load_sessions(tmp_path / "missing.json") == []


def test_save_sessions_rejects_multiple_running_sessions(tmp_path: Path) -> None:
    started_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    sessions = [
        Session(task_id=1, title="First", started_at=started_at),
        Session(task_id=2, title="Second", started_at=started_at),
    ]

    with pytest.raises(StorageError, match="Only one running session"):
        save_sessions(tmp_path / "worklog.json", sessions)


def test_active_session_returns_none_when_no_session_is_running() -> None:
    assert active_session([]) is None
