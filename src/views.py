import datetime
import json
from pathlib import Path
import pandas as pd

# Настройка логирования
from logger_settings import get_logger
from src.decorators import log
from src.utils import read_excel_file, common_information, get_top_five_transactions, get_stock_prices, \
    get_exchange_rates, get_greeting

logger = get_logger()

BASEDIR = Path(__file__).parent.parent.resolve()
file_path = str(BASEDIR / "data" / "operations.xlsx")

transaction_for_print = [{}]


@log()
def main_views(str_time='datetime'):
    """Главная функция для анализа данных принимает дату в формате строки YYYY-MM-DD HH:MM:SS и
    возвращает общую информацию в формате json о банковских транзакциях за период с начала месяца до этой даты"""
    data = read_excel_file(file_path)
    data_df = pd.DataFrame(data)
    date_obj = datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")
    data_df["datetime"] = pd.to_datetime(data_df["Дата операции"], dayfirst=True)
    json_data = data_df[
        (data_df["datetime"] >= (date_obj - datetime.timedelta(days=date_obj.day - 1))) & (data_df["datetime"] <= date_obj)
        ]

    agg_dict = {
        "greetings": get_greeting('datetime'),
        "cards": common_information(json_data),
        "top_transactions": get_top_five_transactions(json_data),
        "currency_rates": get_stock_prices("user_settings.json"),
        "stock_prices": get_exchange_rates("user_settings.json"),
    }
    return json.dumps(agg_dict, ensure_ascii=False)


print(main_views(str_time="2020-08-11 15:25:00"))



@log()
def final_list(current_date):
    """Функция, формирующая конечный список из готовых данных"""
    generate_json(current_date)
    filtered_cards()
    filtered_top()
    transaction_for_print[0]["greeting"] = get_greeting(current_date)
    transaction_for_print[0]["cards"] = cards
    transaction_for_print[0]["top_transactions"] = top_list
    transaction_for_print[0]["currency_rates"] = add_to_list()
    transaction_for_print[0]["stock_prices"] = get_current_stock(settings)
    return transaction_for_print


print(final_list("01.11.2021 23:50:17"), sep="\n")


@log()
def analyze_data(date_str='datetime', data_range="M"):
    """Функция для анализа данных."""
    start_date, end_date = get_data_range(date_str, data_range)
    filtered_data = pd.read_excel(file_path)
    filtered_data["Дата операции"] = filtered_data["Дата операции"].astype(str).str.strip()

    try:
        # Преобразуем 'Дата операции' в формат даты и времени
        filtered_data["Дата операции"] = pd.to_datetime(filtered_data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    except Exception as e:
        print(f"Ошибка при преобразовании дат: {e}")

    # Фильтруем данные по дате
    filtered_data = filtered_data[
        (filtered_data["Дата операции"] >= start_date) & (filtered_data["Дата операции"] <= end_date)
    ]
    # Анализ расходов
    expenses_summary = group_expenses(filtered_data)
    total_expenses = filtered_data["Сумма операции"].sum()
    # Анализ поступлений
    income_summary = group_income(filtered_data)
    total_income = filtered_data["Сумма операции"][filtered_data["Сумма операции"] > 0].sum()
    # Получение валютных курсов и цен акций
    try:
        with open(file_path) as f:
            user_settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Ошибка при чтении файла настроек пользователя: {e}")

    currency_rates = get_currency_rates(user_settings["user_currencies"])
    stock_prices = get_stock_prices(user_settings["user_stocks"])
    # Формирование итогового ответа
    result = {
        "Расходы": {"Общая сумма": total_expenses, "Основные": expenses_summary.to_dict(orient="records")},
        "Поступления": {"Общая сумма": total_income, "Основные": income_summary.to_dict(orient="records")},
        "Курс валют": currency_rates,
        "Цены акций": stock_prices,
    }
    return result


# Пример вызова функции анализа данных к веб-странице События
result = analyze_data(date_str="31.12.2021 16:44:00", data_range="M")
print(json.dumps(result, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    #analyze_data(date_str='datetime', data_range)
    #final_list(current_date)
    #main_views(str_time)
    #get_greeting(datetime)
    print('views')
