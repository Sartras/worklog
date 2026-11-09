"""Data models for worklog."""

from dataclasses import dataclass
from datetime import datetime, timedelta


class WorklogError(Exception):
    """Base class for expected worklog errors."""


class SessionError(WorklogError):
    """Raised when a time session operation is invalid."""


@dataclass
class Session:
    """A time-tracking session for one todo task."""

    task_id: int
    title: str
    started_at: datetime
    ended_at: datetime | None = None

    def duration(self, now: datetime) -> timedelta:
        """Return the elapsed time through the end time or the supplied time."""
        end = self.ended_at or now
        if end < self.started_at:
            raise SessionError("Session end cannot be earlier than its start.")
        return end - self.started_at

    def stop(self, now: datetime) -> None:
        """Stop this session at the supplied time."""
        if self.ended_at is not None:
            raise SessionError("Session has already been stopped.")
        if now < self.started_at:
            raise SessionError("Session end cannot be earlier than its start.")
        self.ended_at = now
