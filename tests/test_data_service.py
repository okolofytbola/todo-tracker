"""
Тесты сервисного слоя (data_service.py).
Покрывают: CRUD-операции, валидацию, краевые случаи.
"""
import pytest
import os
import sys
import tempfile

# Чтобы импорты работали из папки tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import data_service as ds


@pytest.fixture(autouse=True)
def tmp_data_file(tmp_path, monkeypatch):
    """Каждый тест работает со своим пустым CSV-файлом."""
    tmp_file = str(tmp_path / "tasks.csv")
    monkeypatch.setattr(ds, "DATA_FILE", tmp_file)
    yield


# ─── add_task ───────────────────────────────────────────────────────────────

class TestAddTask:
    def test_add_basic(self):
        task = ds.add_task("Купить молоко")
        assert task["title"] == "Купить молоко"
        assert task["priority"] == "medium"
        assert task["done"] == "False"
        assert task["id"] == 1

    def test_add_with_priority_high(self):
        task = ds.add_task("Срочная задача", priority="high")
        assert task["priority"] == "high"

    def test_add_with_deadline(self):
        task = ds.add_task("Сдать отчёт", deadline="2025-12-31")
        assert task["deadline"] == "2025-12-31"

    def test_add_empty_title_raises(self):
        with pytest.raises(ValueError, match="пустым"):
            ds.add_task("")

    def test_add_whitespace_title_raises(self):
        with pytest.raises(ValueError, match="пустым"):
            ds.add_task("   ")

    def test_add_invalid_priority_raises(self):
        with pytest.raises(ValueError, match="Приоритет"):
            ds.add_task("Задача", priority="urgent")

    def test_add_invalid_deadline_raises(self):
        with pytest.raises(ValueError, match="формате"):
            ds.add_task("Задача", deadline="31-12-2025")

    def test_add_strips_title(self):
        task = ds.add_task("  Пробелы  ")
        assert task["title"] == "Пробелы"

    def test_add_multiple_increments_id(self):
        t1 = ds.add_task("Первая")
        t2 = ds.add_task("Вторая")
        assert int(t2["id"]) == int(t1["id"]) + 1


# ─── get_all_tasks ───────────────────────────────────────────────────────────

class TestGetAllTasks:
    def test_empty_db_returns_empty_list(self):
        assert ds.get_all_tasks() == []

    def test_returns_all_added(self):
        ds.add_task("А")
        ds.add_task("Б")
        ds.add_task("В")
        assert len(ds.get_all_tasks()) == 3


# ─── get_task_by_id ──────────────────────────────────────────────────────────

class TestGetTaskById:
    def test_existing_task(self):
        ds.add_task("Тест")
        task = ds.get_task_by_id(1)
        assert task is not None
        assert task["title"] == "Тест"

    def test_nonexistent_returns_none(self):
        assert ds.get_task_by_id(999) is None


# ─── delete_task ─────────────────────────────────────────────────────────────

class TestDeleteTask:
    def test_delete_existing(self):
        ds.add_task("Удалить меня")
        assert ds.delete_task(1) is True
        assert ds.get_task_by_id(1) is None

    def test_delete_nonexistent_returns_false(self):
        assert ds.delete_task(42) is False

    def test_delete_does_not_affect_others(self):
        ds.add_task("Первая")
        ds.add_task("Вторая")
        ds.delete_task(1)
        tasks = ds.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Вторая"


# ─── update_task ─────────────────────────────────────────────────────────────

class TestUpdateTask:
    def test_update_title(self):
        ds.add_task("Старое название")
        updated = ds.update_task(1, title="Новое название")
        assert updated["title"] == "Новое название"

    def test_update_priority(self):
        ds.add_task("Задача")
        updated = ds.update_task(1, priority="high")
        assert updated["priority"] == "high"

    def test_update_deadline(self):
        ds.add_task("Задача")
        updated = ds.update_task(1, deadline="2026-01-01")
        assert updated["deadline"] == "2026-01-01"

    def test_update_nonexistent_returns_none(self):
        assert ds.update_task(999, title="Что-то") is None

    def test_update_empty_title_raises(self):
        ds.add_task("Задача")
        with pytest.raises(ValueError, match="пустым"):
            ds.update_task(1, title="")

    def test_update_invalid_priority_raises(self):
        ds.add_task("Задача")
        with pytest.raises(ValueError, match="Приоритет"):
            ds.update_task(1, priority="critical")

    def test_update_invalid_deadline_raises(self):
        ds.add_task("Задача")
        with pytest.raises(ValueError, match="формате"):
            ds.update_task(1, deadline="2026/01/01")


# ─── mark_done ───────────────────────────────────────────────────────────────

class TestMarkDone:
    def test_mark_existing(self):
        ds.add_task("Сделать")
        result = ds.mark_done(1)
        assert result["done"] == "True"

    def test_mark_nonexistent_returns_none(self):
        assert ds.mark_done(99) is None

    def test_done_persists(self):
        ds.add_task("Сделать")
        ds.mark_done(1)
        task = ds.get_task_by_id(1)
        assert task["done"] == "True"


# ─── clear_all ───────────────────────────────────────────────────────────────

class TestClearAll:
    def test_clears_everything(self):
        ds.add_task("Первая")
        ds.add_task("Вторая")
        ds.clear_all()
        assert ds.get_all_tasks() == []
