import json
from pathlib import Path

import pytest

from worklog.todo_source import TodoSourceError, get_task_title, load_tasks


def test_get_task_title_uses_one_based_position(tmp_path: Path) -> None:
    todo_file = tmp_path / "todo.json"
    todo_file.write_text(json.dumps({"tasks": [{"title": "First"}, {"title": "Next"}]}))

    title = get_task_title(2, todo_file)

    assert title == "Next"


def test_load_tasks_rejects_a_missing_title(tmp_path: Path) -> None:
    todo_file = tmp_path / "todo.json"
    todo_file.write_text(json.dumps([{"name": "No title"}]))

    with pytest.raises(TodoSourceError, match="non-empty title"):
        load_tasks(todo_file)


@pytest.mark.parametrize("task_id", [0, 3])
def test_get_task_title_rejects_invalid_id(tmp_path: Path, task_id: int) -> None:
    todo_file = tmp_path / "todo.json"
    todo_file.write_text(json.dumps(["First", "Second"]))

    with pytest.raises(TodoSourceError):
        get_task_title(task_id, todo_file)
