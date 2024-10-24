import os, threading, json
os.chdir(os.path.dirname(os.path.realpath(__file__)))

from bot import bot_start
from google_sheets import carTable

bot_configs = dict()
with open('settings/settings.json', 'r', encoding='utf-8') as file:
    bot_configs = json.load(file)

def telebot_handle():
    bot_start()

if __name__ == '__main__':

    carTable.update()
    telebot_thread = threading.Thread(target=telebot_handle)
    telebot_thread.start()