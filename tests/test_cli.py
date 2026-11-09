import json
from datetime import datetime, timezone, tzinfo
from pathlib import Path

import pytest

from worklog import cli


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz: tzinfo | None = None) -> datetime:
        return cls(2026, 1, 1, 0, 0, 12, tzinfo=tz)


def test_start_displays_task_title_and_saves_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    todo_file = tmp_path / "todo.json"
    worklog_file = tmp_path / "worklog.json"
    todo_file.write_text(json.dumps([{"title": "Write tests"}]))
    monkeypatch.setenv("TODO_FILE", str(todo_file))
    monkeypatch.setenv("WORKLOG_FILE", str(worklog_file))

    result = cli.main(["start", "1"])

    output = capsys.readouterr().out
    saved_data = json.loads(worklog_file.read_text())
    assert result == 0
    assert "Write tests" in output
    assert saved_data["sessions"][0]["title"] == "Write tests"


def test_start_rejects_a_second_running_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    todo_file = tmp_path / "todo.json"
    worklog_file = tmp_path / "worklog.json"
    todo_file.write_text(json.dumps(["Write tests"]))
    monkeypatch.setenv("TODO_FILE", str(todo_file))
    monkeypatch.setenv("WORKLOG_FILE", str(worklog_file))

    cli.main(["start", "1"])
    capsys.readouterr()
    result = cli.main(["start", "1"])

    captured = capsys.readouterr()
    assert result == 1
    assert captured.out == ""
    assert "A time session is already running." in captured.err


def test_stop_displays_elapsed_duration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    todo_file = tmp_path / "todo.json"
    worklog_file = tmp_path / "worklog.json"
    todo_file.write_text(json.dumps(["Write tests"]))
    monkeypatch.setenv("TODO_FILE", str(todo_file))
    monkeypatch.setenv("WORKLOG_FILE", str(worklog_file))
    started_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(cli, "datetime", FixedDateTime)
    worklog_file.write_text(
        json.dumps(
            {
                "sessions": [
                    {
                        "task_id": 1,
                        "title": "Write tests",
                        "started_at": started_at.isoformat(),
                        "ended_at": None,
                    }
                ]
            }
        )
    )

    result = cli.main(["stop"])

    output = capsys.readouterr().out
    saved_data = json.loads(worklog_file.read_text())
    assert result == 0
    assert "Erfasste Dauer: 0:00:12" in output
    assert saved_data["sessions"][0]["ended_at"] is not None


def test_stop_without_running_session_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("WORKLOG_FILE", str(tmp_path / "worklog.json"))

    result = cli.main(["stop"])

    captured = capsys.readouterr()
    assert result == 1
    assert captured.out == ""
    assert "No time session is running." in captured.err
