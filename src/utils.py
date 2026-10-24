import json
import logging
import os
from builtins import isinstance
from datetime import datetime, timedelta
from typing import Any
from urllib.request import urlopen
import numpy
import pandas as pd
from pathlib import Path
import requests
from dotenv import load_dotenv


# Настройка логирования
from logger_settings import get_logger
from src.decorators import log

logger = get_logger()


get_excel_df_logger = logging.getLogger("get_excel_df")
top_5_operations_logger = logging.getLogger("top_5_operations")
common_information_logger = logging.getLogger("common_information")
get_exchange_rate_logger = logging.getLogger("get_exchange_rate")
get_stock_price_logger = logging.getLogger("get_stock_price")

BASEDIR = Path(__file__).parent.parent.resolve()
file_path = str(BASEDIR / "data" / "operations.xlsx")


@log()
def get_data_range(date_str, data_range):
    """ Функция преобразования входной строки, если время не задано"""
    if len(date_str) == 10:  # формат 'DD.MM.YYYY'
        date_str += " 00:00:00"
        logging.debug(f"Преобразована строка даты: {date_str}")

    # Теперь можно безопасно разбирать строку
    parsed_date = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
    logging.debug(f"Разобранная дата: {parsed_date}")

    if data_range == "M":
        start_date = parsed_date.replace(hour=0, minute=0, second=0)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(seconds=1)
        end_date = end_date.replace(hour=23, minute=59, second=59)
        logging.debug(f"Месячный период: {start_date} - {end_date}")

    elif data_range == "W":
        start_date = parsed_date - timedelta(days=parsed_date.weekday())  # Понедельник
        end_date = start_date + timedelta(days=6)  # Воскресенье
        end_date = end_date.replace(hour=23, minute=59, second=59)
        logging.debug(f"Недельный период: {start_date} - {end_date}")

    elif data_range == "Y":
        start_date = parsed_date.replace(month=1, day=1, hour=0, minute=0, second=0)
        end_date = parsed_date.replace(month=12, day=31, hour=23, minute=59, second=59)
        logging.debug(f"Годовой диапазон: {start_date} - {end_date}")

    elif data_range == "ALL":
        # Логика для ALL
        start_date = datetime(2021, 1, 1, 16, 44, 0)
        end_date = parsed_date
        logging.debug(f"Период даты и времени: {start_date} - {end_date}")

    else:
        logging.error("Недопустимый период")
        raise ValueError("Invalid period")

    return start_date, end_date


@log()
def get_greeting() -> str:
    """Функция возвращает приветствие в зависимости от текущего времени"""
    # Получаем текущее время
    current_time = datetime.now().time()
    print(f"Текущее время равно: {current_time}")

    # Определяем время для приветствий
    morning_start = datetime.strptime("06:00", "%H:%M").time()
    afternoon_start = datetime.strptime("12:00", "%H:%M").time()
    evening_start = datetime.strptime("16:00", "%H:%M").time()
    night_start = datetime.strptime("23:00", "%H:%M").time()

    # Определяем приветствие на основе текущего времени
    if morning_start <= current_time < afternoon_start:
        day = "Доброе утро!"
        return day
    elif afternoon_start <= current_time < evening_start:
        day = "Добрый день!"
        return day
    elif evening_start <= current_time < night_start:
        day = "Добрый вечер!"
        return day
    else:
        day = "Доброй ночи!"
        return day


@log()
def read_excel_file(file_path) -> Union[None, pd.DataFrame]:
    """
    Чтение файла Excel и получение номера карты и
    :param file_path: расположение файла
    :return: файл DataFrame
    """
    # Проверка на формат файла
    if file_path is None:
        logger.warning("Файл не найден")
        return None
    if not (file_path.endswith(".xlsx") or file_path.endswith(".xls")):  # проверка формата файла (окончание .xlsx)
        logger.warning("Неверный формат файла")
        return None
    try:
        excel_datas = pd.read_excel(file_path)
        return excel_datas
    except Exception as e:
        logger.warning(f"Ошибка файла {e}")
        return None

@log()
def get_operations_excel() -> list[dict]:
    """ Функция возвращает список транзакций (словарь или датафрейм), загруженный из внешнего файла Excel
    и возвращает их в формате DataFrame за период с начала месяца до заданной даты в формате YYYY-MM-DD HH:MM:SS"""
    current_transaction = []
    get_excel_file = pd.read_excel("./data/operations.xlsx")
    if formatting == "dataframe":
        logger.debug('Convert to dataframe successfully')
        return get_excel_file
    elif formatting == "dict":
        for transaction in get_excel_file.to_dict(orient="records"):
            transaction = {
                key: (
                    None if isinstance(value, float) and numpy.isnan(value) else value
                )
                for key, value in transaction.items()
            }
            current_transaction.append(transaction)
        logger.debug('Convert to dict successfully')
        return current_transaction
    else:
        logger.error('Incorrect data')
        raise ValueError("Invalid format specified. Use 'dataframe' or 'dict'.")


current_transactions = []
cards = []
top_list = []


@log()
def generate_json(current_date):
    """Функция, возвращающая отфильтрованные по дате транзакции"""
    for transaction in get_excel("dict"):
        if (
            str(transaction["Дата платежа"])[2:10] == current_date[2:10]
            and str(transaction["Дата платежа"])[:2] <= current_date[:2]
        ):
            current_transactions.append(transaction)
    logger.debug('Correct data payment')
    return current_transactions


@log()
def filtered_cards():
    """Функция, возвращающая правильный список карт"""
    for transaction in current_transactions:
        card = {
            "last_digit": transaction["Номер карты"],
            "total_spent": transaction["Сумма операции"],
            "cashback": round(transaction["Сумма операции"] / 100, 2),
        }
        cards.append(card)
    logger.debug('Correct filtered cards')
    return cards


@log()
def common_information(list_dict: list[dict]) -> list[Any] | None:
    """Функция возвращает общую информацию по всем транзакциям"""
    try:
        list_data = []
        df = pd.DataFrame(list_dict)
        df["datetime"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
        grouped_data = df.groupby("Номер карты").agg({"Сумма платежа": "sum", "Кэшбэк": "sum"}).reset_index()
        grouped_data["Сумма платежа"] = grouped_data["Сумма платежа"].abs()
        for _, row in grouped_data.iterrows():
            dic = {"last_digits": (row["Номер карты"])[-4:], "total_spent": row["Сумма платежа"],
                   "cashback": round((row["Кэшбэк"]) / (row["Сумма платежа"]) * 100, 2)}
            list_data.append(dic)
        common_information_logger.info("Успешно сформирована общая информация по всем транзакциям")
        return list_data
    except Exception as e:
        get_exchange_rate_logger.warning(
            f"""!!!! Не удалось сформировать отчет проверьте поля списка {list_dict}.
        Ошибка - {e}"""
        )


@log()
def get_top_five_transactions(transaction_lst_: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Принимает список словарей транзакций. Формирует список Топ-5 транзакций по сумме платежа.
    Отдает данные по типу:
              [{"date": "21.12.2021",
              "amount": 1198.23,
              "category": "Переводы",
          "description": "Перевод Кредитная карта. ТП 10.2 RUR"}]
        """
    df = pd.DataFrame(transaction_lst_)
    df = df.dropna(subset="Номер карты")
    # print(df)
    transaction_sorted = df[
        ["Дата платежа", "Сумма платежа", "Категория", "Описание", "Сумма операции с округлением"]].sort_values(
        by="Сумма операции с округлением", ascending=False)
    transaction_top_5 = transaction_sorted.nlargest(5, "Сумма операции с округлением")
    transaction_top_5_ = transaction_top_5[["Дата платежа", "Сумма платежа", "Категория", "Описание"]]
    transaction_top_5_ = transaction_top_5_.rename(columns={
        'Дата платежа': 'date',
        'Сумма платежа': 'amount',
        'Категория': 'category',
        'Описание': 'description'
        })
    top_transactions = transaction_top_5_.to_dict('records')  # type: ignore[assignment]

    return top_transactions


@log()
def get_currency_rates(currencies):
    rates = {}
    for currency in currencies:
        logging.debug(f"Запрос курсов для валюты: {currency}")
        try:
            response = requests.get(
                f"https://v6.exchangerate-api.com/v6/ed5608baba940bd1aa75173b/latest/USD {currency}"
            )
            response.raise_for_status()
            rates[currency] = response.json().get("rates", {})
            logging.info(f"Успешно получены курсы для {currency}: {rates[currency]}")
        except requests.RequestException as e:
            logging.error(f"Ошибка при получении курса для {currency}: {e}")
            rates[currency] = {}
    return rates


@log()
def get_exchange_rates(json_file) -> list[Any] | None:
    """получает json-файл с кодировкой иностранных валют и url-ссылку по обменным курсам валют и
    возвращает значения текущих котировок этих валют"""
    try:
        total_list = []
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        response = requests.get(url)
        if response.status_code == 200:
            data_curr = response.json()
            with open((os.path.join("../data/", json_file)), "r") as file:
                user_shares = json.load(file)
                for i in user_shares["user_currencies"]:
                    dic = {"currency": i, "exchange_rate": data_curr["Valute"][i]["Value"]}
                    total_list.append(dic)
            get_exchange_rate_logger.info(
                f'Успешно сформированы котировки {', '.join(user_shares["user_currencies"])} к рублю'
            )
            return total_list
    except Exception as e:
        get_exchange_rate_logger.warning(f"!!!! Не удалось отобразить котировки. Ошибка - {e}")
        return []


@log()
def get_stock_prices(json_file: str) -> list[Any] | None:
    """Получает json-файл с наименованиями ценных бумаг и url-ссылку на котировки ценных бумаг и
    возвращает их текущие котировки."""
    logging.debug(f"Запрос цены для акции: {stock}")
    try:
        load_dotenv()
        api_key = os.getenv("API_KEY")
        total_list = []
        url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}"
        response = urlopen(url)
        data = response.read().decode("utf-8")
        stock_list = json.loads(data)
        with open((os.path.join("../data/", json_file)), "r") as file:
            user_shares = json.load(file)
        for i in user_shares["user_stocks"]:
            for q in stock_list:
                if i == q["symbol"]:
                    dic = {"stock": i, "price": q["price"]}
                    total_list.append(dic)
        get_stock_price_logger.info(
            f'Успешно сформированы котировки акций {', '.join(user_shares["user_stocks"])} к рублю'
        )
        return total_list
    except Exception as e:
        get_stock_price_logger.warning(f"!!!! Не удалось отобразить котировки акции. Ошибка - {e}")


@log()
def group_expenses(filtered_data):
    """Группирует расходы по категориям и возвращает основные категории."""
    logging.debug("Начало группировки расходов")
    expenses_by_category = (
        filtered_data[filtered_data["Сумма операции"] < 0].groupby("Категория")["Сумма операции"].sum().reset_index()
    )
    expenses_by_category["Сумма операции"] = expenses_by_category["Сумма операции"].round(0)
    top_expenses = expenses_by_category.nlargest(7, "Сумма операции")
    other_expenses_sum = expenses_by_category.loc[
        ~expenses_by_category["Категория"].isin(top_expenses["Категория"]), "Сумма операции"
    ].sum()

    other_expenses = pd.DataFrame({"Категория": ["Остальное"], "Сумма операции": [other_expenses_sum]})
    combined_expenses = pd.concat([top_expenses, other_expenses], ignore_index=True)

    logging.info("Группировка расходов завершена")
    return combined_expenses


@log()
def group_income(filtered_data):
    """Группирует поступления по категориям и возвращает основные категории."""
    logging.debug("Начало группировки поступлений")
    income_by_category = (
        filtered_data[filtered_data["Сумма операции"] > 0].groupby("Категория")["Сумма операции"].sum().reset_index()
    )
    income_by_category["Сумма операции"] = income_by_category["Сумма операции"].round(0)
    top_income = income_by_category.nlargest(7, "Сумма операции")
    other_income_sum = income_by_category.loc[
        ~income_by_category["Категория"].isin(top_income["Категория"]), "Сумма операции"].sum()
    other_income = pd.DataFrame({"Категория": ["Остальное"], "Сумма операции": [other_income_sum]})
    combined_income = pd.concat([top_income, other_income], ignore_index=True)

    logging.info("Группировка поступлений завершена")
    return combined_income


if __name__ == '__main__':
    #group_income(filtered_data)
    #group_expenses(filtered_data)
    #get_stock_prices(json_file)
    #get_exchange_rates(json_file)
    #get_currency_rates(currencies)
    #get_top_five_transactions(transaction_lst)
    #common_information(list_dict)
    #read_excel_file(path)
    #filtered_cards()
    #generate_json(current_date)
    #get_operations_excel()
    #get_greeting()
    #get_data_range(date_str, data_range)
    print('utils')
