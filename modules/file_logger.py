import logging
from .constants import get_date_str

logger = logging.Logger

def init():
    global logger
    # Создаем логгер
    logger = logging.getLogger('custom_logger')
    logger.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования

    # Создаем обработчик для записи логов в файл
    file_handler = logging.FileHandler(f'logs/{get_date_str()}.txt',encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования для обработчика

    # Задаем формат логов
    formatter = logging.Formatter('%(asctime)s %(levelname)-7s %(module)s.%(funcName)s(): %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
    file_handler.setFormatter(formatter)

    if False:
        # Обработчик для вывода логов в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Добавляем обработчик в логгер
    logger.addHandler(file_handler)

init()
