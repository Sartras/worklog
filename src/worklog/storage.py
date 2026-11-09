"""Load and save worklog sessions."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from worklog.models import Session, WorklogError


class StorageError(WorklogError):
    """Raised when worklog session data cannot be read or written."""


def load_sessions(path: Path) -> list[Session]:
    """Load sessions from the worklog file, returning an empty list if absent."""
    if not path.exists():
        return []

    try:
        with path.open(encoding="utf-8") as worklog_file:
            data: Any = json.load(worklog_file)
        records = data["sessions"]
        if not isinstance(records, list):
            raise ValueError("sessions must be a list")
        sessions = [_session_from_record(record) for record in records]
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise StorageError(f"Cannot read worklog data from {path}: {error}") from error

    if sum(session.ended_at is None for session in sessions) > 1:
        raise StorageError("Worklog data contains more than one running session.")
    return sessions


def save_sessions(path: Path, sessions: list[Session]) -> None:
    """Save sessions to the worklog file."""
    if sum(session.ended_at is None for session in sessions) > 1:
        raise StorageError("Only one running session can be saved.")

    data = {"sessions": [_record_from_session(session) for session in sessions]}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as worklog_file:
            json.dump(data, worklog_file, ensure_ascii=False, indent=2)
            worklog_file.write("\n")
    except OSError as error:
        raise StorageError(f"Cannot write worklog data to {path}: {error}") from error


def active_session(sessions: list[Session]) -> Session | None:
    """Return the running session, if one exists."""
    running = [session for session in sessions if session.ended_at is None]
    if len(running) > 1:
        raise StorageError("Worklog data contains more than one running session.")
    return running[0] if running else None


def _session_from_record(record: Any) -> Session:
    if not isinstance(record, dict):
        raise ValueError("each session must be an object")

    task_id = record["task_id"]
    title = record["title"]
    started_at = record["started_at"]
    ended_at = record.get("ended_at")
    if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id < 1:
        raise ValueError("task_id must be a positive integer")
    if not isinstance(title, str) or not title:
        raise ValueError("title must be a non-empty string")
    if not isinstance(started_at, str):
        raise ValueError("started_at must be a datetime string")
    if ended_at is not None and not isinstance(ended_at, str):
        raise ValueError("ended_at must be a datetime string or null")

    return Session(
        task_id=task_id,
        title=title,
        started_at=datetime.fromisoformat(started_at),
        ended_at=datetime.fromisoformat(ended_at) if ended_at else None,
    )


def _record_from_session(session: Session) -> dict[str, int | str | None]:
    return {
        "task_id": session.task_id,
        "title": session.title,
        "started_at": session.started_at.isoformat(),
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
    }
