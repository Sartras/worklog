"""Read todo-cli tasks from their JSON file."""

import json
from pathlib import Path
from typing import Any

from worklog.models import WorklogError


class TodoSourceError(WorklogError):
    """Raised when the todo-cli task file cannot be read."""


def load_tasks(path: Path) -> list[str]:
    """Load task titles from a JSON array or an object containing a tasks array."""
    try:
        with path.open(encoding="utf-8") as todo_file:
            data: Any = json.load(todo_file)
    except (OSError, json.JSONDecodeError) as error:
        raise TodoSourceError(f"Cannot read tasks from {path}: {error}") from error

    tasks = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(tasks, list):
        raise TodoSourceError("Todo file must contain a JSON array of tasks.")

    titles: list[str] = []
    for index, task in enumerate(tasks, start=1):
        title = task.get("title") if isinstance(task, dict) else task
        if not isinstance(title, str) or not title.strip():
            raise TodoSourceError(f"Task {index} must have a non-empty title.")
        titles.append(title)
    return titles


def get_task_title(task_id: int, path: Path) -> str:
    """Return a task title using its one-based position in the todo list."""
    if task_id < 1:
        raise TodoSourceError("Task ID must be a positive number.")

    tasks = load_tasks(path)
    if task_id > len(tasks):
        raise TodoSourceError(f"Task ID {task_id} does not exist.")
    return tasks[task_id - 1]
