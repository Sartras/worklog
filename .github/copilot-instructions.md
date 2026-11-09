# Projekt: worklog
Kommandozeilen-Tool zur Zeiterfassung für Aufgaben aus todo-cli.

# Datenquellen
- **Aufgaben** werden aus der todo-cli-Datei gelesen: Pfad aus der
  Umgebungsvariable `TODO_FILE`, sonst `~/.todo.json`.
  Diese Datei wird **nur gelesen, niemals geschrieben**, weil sie todo-cli gehört.
- **Zeiteinträge** werden in einer eigenen Datei gespeichert: Pfad aus
  `WORKLOG_FILE`, sonst `~/.worklog.json`.
- Aufgaben-IDs sind die Positionen aus `todo list` (beginnend bei 1).
  Beim Start wird zusätzlich der Aufgabentitel gespeichert, da sich
  Positionen ändern können.

# Projektstruktur
- `src/worklog/models.py` – Datenmodell (dataclass `Session`)
- `src/worklog/todo_source.py` – Lesen der todo-cli-Aufgaben
- `src/worklog/storage.py` – Laden und Speichern der Zeiteinträge
- `src/worklog/cli.py` – argparse-Befehle, Einstiegspunkt `main()`
- `tests/` – eine Testdatei pro Modul

# Befehle
- Installation: `.venv/bin/pip install -e ".[dev]"`
- Tests: `.venv/bin/python -m pytest`
- Lint: `.venv/bin/ruff check .`
- Format: `.venv/bin/ruff format .`

Eine Aufgabe ist erst erledigt, wenn Tests und Lint fehlerfrei durchlaufen.

# Projektregeln
- Ausgaben mit `print()` nur in `cli.py`
- Die aktuelle Zeit nie direkt in der Logik mit `datetime.now()` holen, sondern
  als Parameter `now: datetime` übergeben. Nur `cli.py` ruft `datetime.now()` auf.
- Es kann immer nur eine laufende Erfassung geben.
- Keine Features bauen, die nicht angefragt wurden.