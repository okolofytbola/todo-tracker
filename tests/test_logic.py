"""
Тесты бизнес-логики (logic.py).
Покрывают: фильтрацию, поиск, статистику, просроченные задачи.
"""
import pytest
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import data_service as ds
import logic


@pytest.fixture(autouse=True)
def tmp_data_file(tmp_path, monkeypatch):
    tmp_file = str(tmp_path / "tasks.csv")
    monkeypatch.setattr(ds, "DATA_FILE", tmp_file)
    yield




class TestFilterByPriority:
    def test_filter_high(self):
        ds.add_task("Срочная", priority="high")
        ds.add_task("Обычная", priority="medium")
        result = logic.filter_by_priority("high")
        assert len(result) == 1
        assert result[0]["title"] == "Срочная"

    def test_filter_returns_empty_if_none(self):
        ds.add_task("Задача", priority="low")
        assert logic.filter_by_priority("high") == []

    def test_invalid_priority_raises(self):
        with pytest.raises(ValueError):
            logic.filter_by_priority("critical")



class TestFilterByStatus:
    def test_filter_pending(self):
        ds.add_task("Задача")
        result = logic.filter_by_status(False)
        assert len(result) == 1

    def test_filter_done(self):
        ds.add_task("Задача")
        ds.mark_done(1)
        result = logic.filter_by_status(True)
        assert len(result) == 1
        assert result[0]["done"] == "True"

    def test_done_not_in_pending(self):
        ds.add_task("Задача")
        ds.mark_done(1)
        assert logic.filter_by_status(False) == []



class TestSearchByTitle:
    def test_finds_by_substring(self):
        ds.add_task("Купить молоко")
        ds.add_task("Сделать отчёт")
        result = logic.search_by_title("молоко")
        assert len(result) == 1
        assert result[0]["title"] == "Купить молоко"

    def test_case_insensitive(self):
        ds.add_task("ВАЖНАЯ задача")
        result = logic.search_by_title("важная")
        assert len(result) == 1

    def test_empty_keyword_raises(self):
        with pytest.raises(ValueError, match="пустым"):
            logic.search_by_title("")

    def test_whitespace_keyword_raises(self):
        with pytest.raises(ValueError, match="пустым"):
            logic.search_by_title("   ")

    def test_no_results(self):
        ds.add_task("Купить хлеб")
        assert logic.search_by_title("молоко") == []



class TestGetOverdueTasks:
    def test_past_deadline_is_overdue(self):
        yesterday = str(date.today() - timedelta(days=1))
        ds.add_task("Просроченная", deadline=yesterday)
        result = logic.get_overdue_tasks()
        assert len(result) == 1

    def test_future_deadline_not_overdue(self):
        tomorrow = str(date.today() + timedelta(days=1))
        ds.add_task("Не просроченная", deadline=tomorrow)
        assert logic.get_overdue_tasks() == []

    def test_done_task_not_overdue(self):
        yesterday = str(date.today() - timedelta(days=1))
        ds.add_task("Выполненная просрочка", deadline=yesterday)
        ds.mark_done(1)
        assert logic.get_overdue_tasks() == []

    def test_no_deadline_not_overdue(self):
        ds.add_task("Без срока")
        assert logic.get_overdue_tasks() == []



class TestSortedByPriority:
    def test_order_high_medium_low(self):
        ds.add_task("Низкий", priority="low")
        ds.add_task("Средний", priority="medium")
        ds.add_task("Высокий", priority="high")
        result = logic.get_tasks_sorted_by_priority()
        priorities = [t["priority"] for t in result]
        assert priorities == ["high", "medium", "low"]



class TestWeeklyStats:
    def test_empty_stats(self):
        stats = logic.weekly_stats()
        assert stats == {"total": 0, "done": 0, "pending": 0, "overdue": 0}

    def test_counts_correctly(self):
        yesterday = str(date.today() - timedelta(days=1))
        ds.add_task("Выполненная")
        ds.mark_done(1)
        ds.add_task("Активная")
        ds.add_task("Просроченная", deadline=yesterday)
        stats = logic.weekly_stats()
        assert stats["total"] == 3
        assert stats["done"] == 1
        assert stats["pending"] == 2
        assert stats["overdue"] == 1



class TestDaysUntilDeadline:
    def test_future_deadline(self):
        tomorrow = str(date.today() + timedelta(days=3))
        ds.add_task("Задача", deadline=tomorrow)
        assert logic.days_until_deadline(1) == 3

    def test_past_deadline_negative(self):
        yesterday = str(date.today() - timedelta(days=2))
        ds.add_task("Задача", deadline=yesterday)
        assert logic.days_until_deadline(1) == -2

    def test_no_deadline_returns_none(self):
        ds.add_task("Без дедлайна")
        assert logic.days_until_deadline(1) is None

    def test_nonexistent_task_raises(self):
        with pytest.raises(ValueError, match="не найдена"):
            logic.days_until_deadline(999)
