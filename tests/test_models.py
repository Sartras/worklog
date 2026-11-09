from datetime import datetime, timedelta, timezone

import pytest

from worklog.models import Session, SessionError


def test_duration_uses_supplied_time_for_running_session() -> None:
    started_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    now = started_at + timedelta(minutes=5)
    session = Session(task_id=1, title="Example", started_at=started_at)

    duration = session.duration(now)

    assert duration == timedelta(minutes=5)


def test_stop_sets_end_time() -> None:
    started_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    ended_at = started_at + timedelta(minutes=5)
    session = Session(task_id=1, title="Example", started_at=started_at)

    session.stop(ended_at)

    assert session.ended_at == ended_at


def test_stop_rejects_an_earlier_time() -> None:
    started_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    session = Session(task_id=1, title="Example", started_at=started_at)

    with pytest.raises(SessionError, match="earlier"):
        session.stop(started_at - timedelta(seconds=1))
