from datetime import date
from data_service import get_all_tasks, get_task_by_id

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def filter_by_priority(priority: str) -> list:
    """Возвращает список задач с заданным приоритетом."""
    from data_service import VALID_PRIORITIES
    if priority not in VALID_PRIORITIES:
        raise ValueError("Приоритет должен быть: low, medium или high.")
    return [t for t in get_all_tasks() if t["priority"] == priority]


def filter_by_status(done: bool) -> list:
    """Возвращает выполненные (True) или невыполненные (False) задачи."""
    flag = "True" if done else "False"
    return [t for t in get_all_tasks() if t["done"] == flag]


def search_by_title(keyword: str) -> list:
    """Поиск задач по части названия (регистронезависимый)."""
    if not keyword or not keyword.strip():
        raise ValueError("Ключевое слово не может быть пустым.")
    kw = keyword.strip().lower()
    return [t for t in get_all_tasks() if kw in t["title"].lower()]


def get_overdue_tasks() -> list:
    """Возвращает невыполненные задачи, у которых срок уже прошёл."""
    today = str(date.today())
    result = []
    for t in get_all_tasks():
        if t["done"] == "False" and t["deadline"] and t["deadline"] < today:
            result.append(t)
    return result


def get_tasks_sorted_by_priority() -> list:
    """Возвращает все задачи, отсортированные по приоритету: high → medium → low."""
    tasks = get_all_tasks()
    return sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t["priority"], 99))


def weekly_stats() -> dict:
    """Статистика по задачам: всего, выполнено, просрочено."""
    all_tasks = get_all_tasks()
    total = len(all_tasks)
    done = sum(1 for t in all_tasks if t["done"] == "True")
    overdue = len(get_overdue_tasks())
    pending = total - done
    return {
        "total": total,
        "done": done,
        "pending": pending,
        "overdue": overdue,
    }


def days_until_deadline(task_id: int) -> int | None:
    """
    Возвращает количество дней до дедлайна задачи.
    Отрицательное число — задача просрочена.
    None — дедлайн не задан.
    """
    task = get_task_by_id(task_id)
    if task is None:
        raise ValueError(f"Задача с ID {task_id} не найдена.")
    if not task["deadline"]:
        return None
    delta = date.fromisoformat(task["deadline"]) - date.today()
    return delta.days
