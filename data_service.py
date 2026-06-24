import csv
import os
from datetime import date

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "tasks.csv")
FIELDNAMES = ["id", "title", "priority", "deadline", "done", "created_at"]

VALID_PRIORITIES = {"low", "medium", "high"}


def _ensure_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def _next_id(rows: list) -> int:
    if not rows:
        return 1
    return max(int(r["id"]) for r in rows) + 1


def load_all() -> list:
    _ensure_file()
    with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_all(rows: list):
    _ensure_file()
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def add_task(title: str, priority: str = "medium",
             deadline: str = None) -> dict:
    if not title or not title.strip():
        raise ValueError("Название задачи не может быть пустым.")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Приоритет должен быть: low, medium или high.")
    if deadline is not None:
        try:
            date.fromisoformat(deadline)
        except ValueError:
            raise ValueError("Дата должна быть в формате YYYY-MM-DD.")

    rows = load_all()
    row = {
        "id": _next_id(rows),
        "title": title.strip(),
        "priority": priority,
        "deadline": deadline if deadline else "",
        "done": "False",
        "created_at": str(date.today()),
    }
    rows.append(row)
    save_all(rows)
    return row


def get_all_tasks() -> list:
    return load_all()


def get_task_by_id(task_id: int) -> dict | None:
    for row in load_all():
        if int(row["id"]) == task_id:
            return row
    return None


def delete_task(task_id: int) -> bool:
    rows = load_all()
    new_rows = [r for r in rows if int(r["id"]) != task_id]
    if len(new_rows) == len(rows):
        return False
    save_all(new_rows)
    return True


def update_task(task_id: int, title: str = None, priority: str = None,
                deadline: str = None) -> dict | None:
    rows = load_all()
    updated = None
    for row in rows:
        if int(row["id"]) == task_id:
            if title is not None:
                if not title.strip():
                    raise ValueError("Название задачи не может быть пустым.")
                row["title"] = title.strip()
            if priority is not None:
                if priority not in VALID_PRIORITIES:
                    raise ValueError("Приоритет должен быть: low, medium или high.")
                row["priority"] = priority
            if deadline is not None:
                try:
                    date.fromisoformat(deadline)
                except ValueError:
                    raise ValueError("Дата должна быть в формате YYYY-MM-DD.")
                row["deadline"] = deadline
            updated = row
            break
    if updated:
        save_all(rows)
    return updated


def mark_done(task_id: int) -> dict | None:
    rows = load_all()
    updated = None
    for row in rows:
        if int(row["id"]) == task_id:
            row["done"] = "True"
            updated = row
            break
    if updated:
        save_all(rows)
    return updated


def clear_all():
    save_all([])
