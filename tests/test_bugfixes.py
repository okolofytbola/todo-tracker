"""
Регрессионные тесты для исправленных багов (SUPPORT_LOG.md).

BUG-01: поиск не находил задачи с заглавной буквы
BUG-02: обновление задачи с пустым title не выдавало ошибку
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import data_service as ds
import logic


@pytest.fixture(autouse=True)
def tmp_data_file(tmp_path, monkeypatch):
    tmp_file = str(tmp_path / "tasks.csv")
    monkeypatch.setattr(ds, "DATA_FILE", tmp_file)
    yield


def test_bug01_search_case_insensitive():
    """Поиск должен находить задачи независимо от регистра."""
    ds.add_task("КУПИТЬ МОЛОКО")
    result = logic.search_by_title("молоко")
    assert len(result) == 1, "BUG-01: поиск с нижним регистром не находит задачу с верхним"


def test_bug01_search_mixed_case():
    ds.add_task("Сдать Отчёт")
    result = logic.search_by_title("ОТЧЁТ")
    assert len(result) == 1


def test_bug02_update_empty_title_raises():
    """Обновление с пустой строкой должно вызывать ValueError."""
    ds.add_task("Нормальная задача")
    with pytest.raises(ValueError, match="пустым"):
        ds.update_task(1, title="")


def test_bug02_update_whitespace_title_raises():
    ds.add_task("Нормальная задача")
    with pytest.raises(ValueError, match="пустым"):
        ds.update_task(1, title="   ")
