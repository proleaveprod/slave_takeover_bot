import logging

logger = logging.Logger

def init():
    global logger
    # Создаем логгер
    logger = logging.getLogger('custom_logger')
    logger.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования

    # Создаем обработчик для записи логов в файл
    file_handler = logging.FileHandler('logging.info',encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования для обработчика

    # Задаем формат логов
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
    file_handler.setFormatter(formatter)

    # Добавляем обработчик в логгер
    logger.addHandler(file_handler)

init()
