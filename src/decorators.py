import json
from functools import wraps
from typing import Any
from venv import logger
from pathlib import Path
import pandas as pd

BASEDIR = Path(__file__).parent.parent.resolve()
file_path = str(BASEDIR / "data" / "operations.xlsx")


def log(filename: Any = None) -> Any:
    """Запись логов в файл, имя файла обязательный параметр.
    Если имя не указано создаётся информационный файл
    not_specified_name_to_logs
    В логи записывается данные, которые формирует функция."""
    logger.info("Запуск декоратора.")

    def decorator_log(function: Any) -> Any:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = function(*args, **kwargs)
            if not filename:
                write_to_log = (
                    "\n Вы читаете этот текст, так как не указали имя файла для записи логов. \n"
                    "Укажите имя файла и попробуйте ещё раз! \n"
                    "Этот файл можно удалить! Он ни на что не влияет и "
                    "не содержит какой либо информации! \n"
                )

                with open("not_specified_name_to_logs.log", mode="a", encoding="utf-8") as file:
                    file.write(write_to_log)
                return result
            if isinstance(result, pd.DataFrame):
                dt_excel = result.to_dict("records")
                json_result = json.dumps(dt_excel, default=str, ensure_ascii=False, indent=2)
            else:
                json_result = str(result)

            write_to_log = f"\nРезультат работы функции {function.__name__}\n{json_result}"

            with open(filename, mode="a", encoding="utf-8") as file:
                file.write(write_to_log)

            return result

        return wrapper

    return decorator_log
