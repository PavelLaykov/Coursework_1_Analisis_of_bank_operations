import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key_exchange = os.getenv('api_key_exchange')
api_key_stocks = os.getenv('api_key_stocks')


ROOT_DIR = os.path.dirname(__file__)
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
DATA_DIR = os.path.join(ROOT_DIR, 'data')
file_path = os.path.join(DATA_DIR, 'operations.xlsx')
file_path1 = os.path.join(DATA_DIR, 'user_settings.json')

# Проверяем существование файла
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Файл не найден: {file_path}")

# Читаем данные из Excel
filtered_data = pd.read_excel(file_path)

operations_path = os.path.join(DATA_DIR, 'operations.xlsx')
pd.read_excel(operations_path)

BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR.joinpath('data/my_operations.xlsx')
JSON_PATH = BASE_DIR.joinpath('user_settings.json')
LOG_PATH = BASE_DIR.joinpath('logs/app.log')
REPORTS_PATH = BASE_DIR.joinpath('reports.json')
