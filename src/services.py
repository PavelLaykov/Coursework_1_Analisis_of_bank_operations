import json
from typing import Union
from collections import defaultdict
import datetime
import numpy as np
import pandas as pd
from pathlib import Path
from functools import reduce

# Настройка логирования
from logger_settings import get_logger
from src.decorators import log

logger = get_logger()

BASEDIR = Path(__file__).parent.parent.resolve()
file_path = str(BASEDIR / "data" / "operations.xlsx")

@log()
def get_beneficial_cashback_categories(data, year, month):
    """
    Функция «Выгодные категории повышенного кешбэка»

    :param data: Список транзакций
    :param year: Год для анализа
    :param month: Месяц для анализа
    :return: JSON строка с анализом кэшбэка по категориям
    """

    logger.info("Начинается анализ категорий кешбэка за %d-%02d", year, month)

    # Функция для фильтрации транзакций по году и месяцу
    is_in_month = (
        lambda x: datetime.strptime(x["date"], "%Y-%m-%d").year == year
        and datetime.strptime(x["date"], "%Y-%m-%d").month == month
    )

    filtered_transactions = list(filter(is_in_month, data))
    logger.info("Отфильтрованные транзакции: %s", filtered_transactions)


    # Функция для аккумулирования сумм по категориям
    def accumulate(acc, transaction):
        category = transaction["category"]
        amount = abs(transaction["amount"])
        acc[category] += amount
        return acc

    category_cashback = reduce(accumulate, filtered_transactions, defaultdict(int))

    # Формируем кэшбэк (1% от суммы) и превращаем его в обычный словарь
    cashback = {category: round(amount * 0.01) for category, amount in category_cashback.items()}

    logger.info("Сумма cashback: %s", cashback)

    return json.dumps(cashback, ensure_ascii=False, indent=4)


@log()
def most_profit_cashback(transactions: list[dict], year, month: Union[int, str]) -> str:
    """Функция возвращает повышенные категории кэшбэка из списка транзакций за определенные месяц и год"""
    try:
        if int(month) < 1 or int(month) > 12:
            most_profit_cashback_logger.warning(
                f"!!!! Проверьте корректность номера месяца. Текущее значение месяца - {month}"
            )
            return "[]"
        elif not transactions:
            most_profit_cashback_logger.warning(
                "!!!! Список словарей должен содержать значения. Список словарей не содержит данных"
            )
            return "[]"
        else:
            data = pd.DataFrame(transactions)
            data["datetime"] = pd.to_datetime(data["Дата операции"], dayfirst=True)
            df = data[(data["datetime"].dt.year == year) & (data["datetime"].dt.month == month)]
            data_gr = df.groupby(by="Категория").agg({"Кэшбэк": "sum"})

            final_list = []
            df_final = (
                data_gr[data_gr["Кэшбэк"] != 0].sort_values(by="Кэшбэк", inplace=False, ascending=False).reset_index()
            )
            for _, row in df_final.iterrows():
                dic = {}
                key = f"Категория {row['Категория']}"
                dic[key] = row["Кэшбэк"]
                final_list.append(dic)
            most_profit_cashback_logger.info(
                f"Успешно сформированы данные о повышенных категориях кэшбэка за {month} месяц {year} года"
            )
            return json.dumps(final_list, ensure_ascii=False)
    except Exception as e:
        most_profit_cashback_logger.warning(
            f"""!!!! Не удалось формированы данные о повышенных категориях кэшбэка.
        Ошибка - {e}"""
        )
        return "[]"


@log()
def investment_bank(transactions: list[dict], month: str, limit: int) -> float | None:
    """Возвращает сумму денежных средств, которую можно отложить с трат при заданном размере округления"""
    try:
        if not transactions:
            invest_bank_logger.warning('!!!! Список словарей должен содержать значения.')
        elif limit < 0:
            invest_bank_logger.warning(
                f"!!!! Проверьте корректность порога округления месяца. Текущее значение месяца - {limit}"
            )
        else:
            data = pd.DataFrame(transactions)
            data["datetime"] = pd.to_datetime(data["Дата операции"], dayfirst=True)
            data_obj = datetime.datetime.strptime(month, "%Y-%m")
            data["datetime_new"] = data["datetime"].dt.strftime("%y-%m")
            df_init = data[(data["datetime"].dt.year == data_obj.year) & (data["datetime"].dt.month == data_obj.month)]
            if df_init.empty:
                invest_bank_logger.info("Задайте другую дату")
            else:
                pd.options.mode.chained_assignment = None  # default='warn'
                df_init["Платеж_округл"] = df_init["Сумма платежа"].round(-2).abs()
                df = df_init[df_init["Сумма платежа"] < 0]
                df["Сумма платежа"] = -df["Сумма платежа"]
                df["Инвесткопилка"] = ((df["Сумма платежа"] / limit).apply(np.ceil)) * limit - df["Сумма платежа"]
                invest_bank_logger.info(f"На инвесткопилку можно отложить {round(df['Инвесткопилка'], 2).sum()} д.ед.")
                return float(round(df["Инвесткопилка"], 2).sum())
    except Exception as e:
        invest_bank_logger.warning(f"!!!! Неудачное завершение операции. Ошибка {e}.")


@log()
def search_by_numbers(search_bar: str, list_operations: list[dict]) -> str:
    """
    Функция поиска по телефонным номерам.
    Принимает строку для поиска и список словарей, возвращает JSON-ответ со всеми транзакциями,
    содержащими запрос поиска в поле 'Категория' и 'Описание'.
    Функция возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера.
    """
    services_logger.info("Начало обработки списка словарей")
    try:
        search_bar_f = search_bar.strip().lower()
        result = [
            data
            for data in list_operations
            if
            (isinstance(data.get("Категория", ""), str) and search_bar_f in data.get("Категория", "").strip().lower())
            or (isinstance(data.get("Описание", ""), str) and search_bar_f in data.get("Описание", "").strip().lower())
        ]
        services_logger.info(f"Новый список по запросу: '{search_bar}' создан")
    except Exception as e:
        services_logger.error(f"Ошибка при обработке списка словарей: {e}")
        return json.dumps([])
    return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    #search_by_numbers(search_bar, list_operations)
    #investment_bank(transactions, month, limit)
    #most_profit_cashback(transactions, year, month)
    #accumulate(acc, transaction)
    #get_beneficial_cashback_categories(data, year, month)
    print('services')
