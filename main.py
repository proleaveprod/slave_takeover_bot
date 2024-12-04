import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

from modules.google_sheets import carTable
from modules.bot import bot_start


if __name__ == '__main__':
    carTable.update()
    bot_start()