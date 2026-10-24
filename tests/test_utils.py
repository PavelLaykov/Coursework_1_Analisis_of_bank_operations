from unittest.mock import patch
import pytest
import pandas as pd

from src.utils import (get_data_range, get_exchange_rates,
                       get_greeting, read_excel_file, get_stock_prices, get_top_five_transactions)


def test_top_five_transactions(excel_data: list[dict]) -> None:
    """Тест вывода топ-5 транзакций."""

    data = get_top_five_transactions(pd.DataFrame(excel_data))
    assert data == [
        {"amount": 9700.0, "category": "Пополнения", "date": "25.01.2018", "description": "Перевод с карты"},
        {"amount": 5748.0, "category": "Авиабилеты", "date": "25.01.2018", "description": "Aviacassa"},
        {"amount": 375.0, "category": "Транспорт", "date": "26.01.2018", "description": "Яндекс Такси"},
        {"amount": 325.0, "category": "Фастфуд", "date": "26.01.2018", "description": "OOO Fruittella"},
        {"amount": 295.0, "category": "Фастфуд", "date": "27.01.2018", "description": "OOO Fruittella"},
    ]


def test_get_greeting() -> None:
    date = get_greeting("2022-02-12 12:12:12")
    assert date == "Доброе утро"
    date = get_greeting("2022-02-12 00:12:12")
    assert date == "Доброй ночи"
    date = get_greeting("2022-02-12 14:12:12")
    assert date == "Добрый день"
    date = get_greeting("2022-02-12 20:12:12")
    assert date == "Добрый вечер"


def test_read_excel_file() -> None:
    assert read_excel_file("") is None


def test_get_data_range() -> None:
    assert get_data_range("") == []


def test_get_top_five_transactions(sample_df: pd.DataFrame) -> None:
    """Тест вывода топ-5 транзакций."""
    assert get_top_five_transactions(sample_df) == [
        {"cashback": 2.0, "last_digits": "1111", "total_spent": 200.0},
        {"cashback": 3.0, "last_digits": "2222", "total_spent": 300.0},
        {"cashback": 4.0, "last_digits": "3333", "total_spent": 400.0},
        {"cashback": 5.0, "last_digits": "4444", "total_spent": 500.0},
        {"cashback": 1.0, "last_digits": "5091", "total_spent": 100.0},
        {"cashback": 6.0, "last_digits": "5555", "total_spent": 600.0},
        {"cashback": 7.0, "last_digits": "6666", "total_spent": 700.0},
        {"cashback": 8.0, "last_digits": "7777", "total_spent": 800.0},
        {"cashback": 9.0, "last_digits": "8888", "total_spent": 900.0},
    ]


def test_get_exchange_rates() -> None:
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok", "values": [{"close": "100"}]}
        assert get_exchange_rates() == [{"currency": "USD", "rate": 100.0}, {"currency": "EUR", "rate": 100.0}]


def tests_get_stock_prices() -> None:
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok", "values": [{"price": 222.00}]}
        assert get_stock_prices() == []
