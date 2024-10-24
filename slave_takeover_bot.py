import os, threading, json
os.chdir(os.path.dirname(os.path.realpath(__file__)))

from file_logger import logger
print("Main: Program is started")
logger.info('Main: Program is started')

from bot import bot_start
from google_sheets import carTable

bot_configs = dict()
with open('settings/settings.json', 'r', encoding='utf-8') as file:
    bot_configs = json.load(file)

if __name__ == '__main__':
    carTable.update()
    bot_start()