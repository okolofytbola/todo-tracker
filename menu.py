import os
import sys
from datetime import date

import data_service as ds
import logic


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_task(task: dict):
    status = "✓" if task["done"] == "True" else "○"
    deadline_str = f"  Срок: {task['deadline']}" if task["deadline"] else ""
    print(f"  [{status}] #{task['id']} [{task['priority'].upper()}] {task['title']}{deadline_str}")


def print_tasks(tasks: list, title: str = "Задачи"):
    print(f"\n=== {title} ({len(tasks)}) ===")
    if not tasks:
        print("  Нет задач.")
        return
    for t in tasks:
        print_task(t)


# ─── Меню добавления ────────────────────────────────────────────────────────

def menu_add():
    print("\n--- Добавить задачу ---")
    title = input("Название задачи: ").strip()
    if not title:
        print("Ошибка: название не может быть пустым.")
        return

    print("Приоритет (low / medium / high) [по умолчанию medium]: ", end="")
    priority = input().strip().lower() or "medium"

    print(f"Дедлайн (YYYY-MM-DD) [Enter — без срока]: ", end="")
    deadline_raw = input().strip()
    deadline = deadline_raw if deadline_raw else None

    try:
        task = ds.add_task(title, priority, deadline)
        print(f"✓ Задача #{task['id']} добавлена.")
    except ValueError as e:
        print(f"Ошибка: {e}")


# ─── Меню просмотра ─────────────────────────────────────────────────────────

def menu_view():
    print("\n--- Список задач ---")
    print("1. Все задачи")
    print("2. По приоритету")
    print("3. Только невыполненные")
    print("4. Только выполненные")
    print("5. Просроченные")
    print("6. Все задачи по приоритету (сортировка)")
    choice = input("Выбор: ").strip()

    if choice == "1":
        print_tasks(ds.get_all_tasks(), "Все задачи")
    elif choice == "2":
        p = input("Приоритет (low/medium/high): ").strip().lower()
        try:
            print_tasks(logic.filter_by_priority(p), f"Приоритет: {p}")
        except ValueError as e:
            print(f"Ошибка: {e}")
    elif choice == "3":
        print_tasks(logic.filter_by_status(False), "Невыполненные")
    elif choice == "4":
        print_tasks(logic.filter_by_status(True), "Выполненные")
    elif choice == "5":
        print_tasks(logic.get_overdue_tasks(), "Просроченные")
    elif choice == "6":
        print_tasks(logic.get_tasks_sorted_by_priority(), "По приоритету")
    else:
        print("Неверный выбор.")


# ─── Поиск ──────────────────────────────────────────────────────────────────

def menu_search():
    print("\n--- Поиск задачи ---")
    kw = input("Введите часть названия: ").strip()
    try:
        results = logic.search_by_title(kw)
        print_tasks(results, f"Результаты поиска по «{kw}»")
    except ValueError as e:
        print(f"Ошибка: {e}")


# ─── Отметить выполненной ───────────────────────────────────────────────────

def menu_done():
    print("\n--- Отметить выполненной ---")
    try:
        task_id = int(input("ID задачи: "))
        result = ds.mark_done(task_id)
        if result:
            print(f"✓ Задача #{task_id} отмечена как выполненная.")
        else:
            print(f"Задача #{task_id} не найдена.")
    except ValueError:
        print("Ошибка: введите числовой ID.")


# ─── Редактирование ─────────────────────────────────────────────────────────

def menu_edit():
    print("\n--- Редактировать задачу ---")
    try:
        task_id = int(input("ID задачи: "))
    except ValueError:
        print("Ошибка: введите числовой ID.")
        return

    task = ds.get_task_by_id(task_id)
    if not task:
        print(f"Задача #{task_id} не найдена.")
        return

    print(f"Текущее название: {task['title']} (Enter — не менять)")
    new_title = input("Новое название: ").strip() or None

    print(f"Текущий приоритет: {task['priority']} (Enter — не менять)")
    new_priority = input("Новый приоритет: ").strip().lower() or None

    print(f"Текущий дедлайн: {task['deadline'] or 'не задан'} (Enter — не менять)")
    new_deadline = input("Новый дедлайн (YYYY-MM-DD): ").strip() or None

    try:
        updated = ds.update_task(task_id, new_title, new_priority, new_deadline)
        if updated:
            print(f"✓ Задача #{task_id} обновлена.")
    except ValueError as e:
        print(f"Ошибка: {e}")


# ─── Удаление ───────────────────────────────────────────────────────────────

def menu_delete():
    print("\n--- Удалить задачу ---")
    try:
        task_id = int(input("ID задачи: "))
        if ds.delete_task(task_id):
            print(f"✓ Задача #{task_id} удалена.")
        else:
            print(f"Задача #{task_id} не найдена.")
    except ValueError:
        print("Ошибка: введите числовой ID.")


# ─── Статистика ─────────────────────────────────────────────────────────────

def menu_stats():
    stats = logic.weekly_stats()
    print("\n=== Статистика ===")
    print(f"  Всего задач:    {stats['total']}")
    print(f"  Выполнено:      {stats['done']}")
    print(f"  Осталось:       {stats['pending']}")
    print(f"  Просрочено:     {stats['overdue']}")


# ─── Главное меню ───────────────────────────────────────────────────────────

def main():
    while True:
        print("\n========== TO-DO ТРЕКЕР ==========")
        print("1. Добавить задачу")
        print("2. Просмотр задач")
        print("3. Поиск по названию")
        print("4. Отметить выполненной")
        print("5. Редактировать задачу")
        print("6. Удалить задачу")
        print("7. Статистика")
        print("0. Выход")
        print("===================================")
        choice = input("Выбор: ").strip()

        if choice == "1":
            menu_add()
        elif choice == "2":
            menu_view()
        elif choice == "3":
            menu_search()
        elif choice == "4":
            menu_done()
        elif choice == "5":
            menu_edit()
        elif choice == "6":
            menu_delete()
        elif choice == "7":
            menu_stats()
        elif choice == "0":
            print("Выход. Удачи!")
            sys.exit(0)
        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()
