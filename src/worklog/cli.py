"""Command-line interface for worklog."""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from worklog.models import Session, SessionError, WorklogError
from worklog.storage import active_session, load_sessions, save_sessions
from worklog.todo_source import get_task_title


def main(argv: Sequence[str] | None = None) -> int:
    """Run the worklog command-line interface."""
    parser = argparse.ArgumentParser(prog="worklog")
    commands = parser.add_subparsers(dest="command", required=True)

    start_parser = commands.add_parser("start", help="start tracking a todo task")
    start_parser.add_argument("id", type=int, help="one-based task position")
    commands.add_parser("stop", help="stop the running time session")
    arguments = parser.parse_args(argv)

    todo_path = Path(os.environ.get("TODO_FILE", Path.home() / ".todo.json"))
    worklog_path = Path(os.environ.get("WORKLOG_FILE", Path.home() / ".worklog.json"))

    try:
        if arguments.command == "start":
            _start(arguments.id, todo_path, worklog_path)
        else:
            _stop(worklog_path)
    except WorklogError as error:
        print(f"Fehler: {error}", file=sys.stderr)
        return 1
    return 0


def _start(task_id: int, todo_path: Path, worklog_path: Path) -> None:
    sessions = load_sessions(worklog_path)
    if active_session(sessions) is not None:
        raise SessionError("A time session is already running.")

    title = get_task_title(task_id, todo_path)
    session = Session(
        task_id=task_id, title=title, started_at=datetime.now(timezone.utc)
    )
    sessions.append(session)
    save_sessions(worklog_path, sessions)
    print(f"Gestartet: {title}")


def _stop(worklog_path: Path) -> None:
    sessions = load_sessions(worklog_path)
    session = active_session(sessions)
    if session is None:
        raise SessionError("No time session is running.")

    ended_at = datetime.now(timezone.utc)
    session.stop(ended_at)
    save_sessions(worklog_path, sessions)
    duration = int(session.duration(ended_at).total_seconds())
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"Erfasste Dauer: {hours}:{minutes:02}:{seconds:02}")
