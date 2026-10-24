import functools
import json
import os
from datetime import datetime
from functools import wraps
from typing import Optional, Any
from pathlib import Path
import pandas as pd
from dateutil.relativedelta import relativedelta
from utils import get_operations_excel


# Настройка логирования
from logger_settings import get_logger
from src.decorators import log

logger = get_logger()

BASEDIR = Path(__file__).parent.parent.resolve()
file_path = str(BASEDIR / "data" / "operations.xlsx")

@log()
def log_report_to_file(filename):
    """Декоратор для записи отчета в файл."""

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            df = func(*args, **kwargs)
            logger.info("Проверка: являются ли данные датафреймом")
            if isinstance(df, pd.DataFrame):
                logger.info("Запись отчёта в файл")
                df.to_json(filename, orient="records", lines=True, force_ascii=False)
            else:
                logger.error("Данные не являются датафреймом. В файл записаны не будут")
            return df

        return inner

    return wrapper


@log()
def date_now():
    """Функция, возвращающая текущую дату"""
    now = datetime.now()
    formatted_date = now.strftime("%d.%m.%Y")
    return formatted_date


@log()
def spending_by_category(transactions_df: pd.DataFrame,
                         category: str,
                         date: Optional[str] = str(datetime.now())) -> pd.DataFrame:
    """Функция, которая возвращает датафрейм с тратами по заданной категории
       за последние три месяца (от переданной даты)."""
    transactions_df['Дата операции'] = pd.to_datetime(transactions_df['Дата операции'], dayfirst=True)
    transactions_by_category = transactions_df[(transactions_df['Дата операции']
                                             <= (pd.to_datetime(date, dayfirst=True) + relativedelta(months=2)))
                                            & (transactions_df['Дата операции'] >= pd.to_datetime(date, dayfirst=True))
                                            & (transactions_df['Категория'].str.upper() == category.upper())]
    trans = pd.DataFrame(transactions_by_category.groupby(['Категория'], as_index=False).
                         agg({'Сумма операции': 'sum'})['Сумма операции'].rename({'Сумма операции': category}))
    print(transactions_by_category.to_dict('records'))
    return trans


@log()
def decorator_with_args(file: str):
    """Функция, которая записывает результаты из spending_by_category"""
    def my_big_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                with open(file, "w", encoding="utf-8") as file_2:
                    json.dump(result.to_dict("records"), file_2, ensure_ascii=False)
                return result
            except FileNotFoundError:
                print("Не получилось записать информацию в файл")
        return wrapper
    return my_big_decorator


@log()
def print_spending_by_date(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        with open(os.path.join("./print_decorators/report_1.txt"), "w"):
            return result.to_string(buf="report_1.txt", header=False)
    return wrapper


@log()
def print_name_spending_by_date(file_name):
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(os.path.join(f"./print_decorators/{file_name}"), "w"):
                return result.to_string(buf=file_name, header=False)
        return wrapper
    return my_decorator


@log()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> Any | None:
    """возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты)"""
    try:
        if date is None:
            date = datetime.now()
        else:
            date = datetime.strptime(date, "%Y-%m-%d")

        transactions["datetime"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
        transactions["day_name"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True).dt.day_name()
        df = transactions[
            (transactions["datetime"] >= (date + relativedelta(months=-3))) & (transactions["datetime"] <= date)
        ].groupby(by="day_name")
        print(df.head(10))
        spending_by_weekday_logger.info("Успешное формирование отчета о средних тратах.")
        return (df["Сумма платежа"].mean().abs().round(2)).to_json()
    except Exception as e:
        spending_by_weekday_logger.warning(f"!!!! Неудачное формирование отчета. Ошибка - {e}")


@log()
def report_decorator(filename=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(filename, "a") as f:
                f.write(f"{result}\n")
            return result

        return wrapper

    return decorator


if __name__ == '__main__':
    #report_decorator(filename)
    #spending_by_weekday(transactions, date)
    #print_name_spending_by_date(file_name)
    #print_spending_by_date(func)
    #decorator_with_args(file)
    #spending_by_category(transactions, category, date)
    #date_now()
    #log_report_to_file(filename)
    result = spending_by_category(
        get_operations_excel(file_path), "Аптеки", "26.07.2019 20:58:55"
    )
    print(result)
