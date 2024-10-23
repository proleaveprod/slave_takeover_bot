import sys,os
sys.path.append(f"{os.path.abspath("")}\\.venv\\Lib\\site-packages")

import threading, time, json, bot
from google_sheets import carTable



bot_configs = dict()
with open('settings\\settings.json', 'r', encoding='utf-8') as file:
    bot_configs = json.load(file)

def telebot_handle():
    bot.bot_start()

if __name__ == '__main__':

    carTable.update()
    telebot_thread = threading.Thread(target=telebot_handle)
    telebot_thread.start()