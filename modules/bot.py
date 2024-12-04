import time, traceback
from functools import wraps
import telebot
from telebot import types
from .file_logger import logger
from .google_sheets import carTable
from .constants import *
from .database  import db

# Инициализация бота
bot = telebot.TeleBot(SETTINGS.get('bot-telegram-token'))

def get_username(msg):
    username = msg.from_user.username
    return str(username)

def brand_menu_markup(region):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)        
    markup.add(types.KeyboardButton("⬅️ Назад"))
    for brand in carTable.brands[region]:
        markup.add(types.KeyboardButton(brand))
    return markup

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):    
    # Создаем клавиатуру с регионами
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    for region in carTable.brands.keys():
        markup.add(types.KeyboardButton(region))

    admin_list = SETTINGS.get('admin_list')
    if message.from_user.id in admin_list:
        markup.add(types.KeyboardButton("🛠 Обновить базу"))

    user_data = db.find(USERS_TABLE, 'id', message.chat.id)
    
    if user_data: # Пользователь уже существует
        user_data = user_data[0]
        user_data['username'] = get_username(message)
        user_data['stage'] = STAGE_ZERO
        user_data['region'] = ''
        user_data['brand'] = ''
        user_data['last_action_date'] = get_date_str()
        db.update(USERS_TABLE, user_data)
    else: # Новый пользователь
        born_date = get_date_str()
        user_data = {
                'id': int(message.chat.id),
                'username': get_username(message),
                'stage': STAGE_ZERO,
                'region': '',
                'brand': '',
                'born_date': born_date,
                'last_action_date': born_date
                }
        logger.warning(f"New user: {message.chat.id} ({get_username(message)})")
        db.add(USERS_TABLE,user_data)

    bot.send_message(message.chat.id, "Выберите регион производителя", reply_markup=markup)

# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    user_data = db.find(USERS_TABLE,'id',message.chat.id)
    
    if(user_data):
        user_data = user_data[0]
    else:
        logger.warning(f"handle_message() No id = {message.chat.id} in database")
        start(message)
        return
    
    if text == "⬅️ Назад":
        if user_data['stage'] == STAGE_BRAND_CHOSEN:
            markup = brand_menu_markup(user_data['region'])
            bot.send_message(message.chat.id, f"Выберите марку автомобиля", reply_markup=markup)
            user_data['stage'] = STAGE_REGION_CHOSEN
            user_data['brand'] = ''
            db.update(USERS_TABLE,user_data)

        else:
            start(message)
        return

    elif text == "🛠 Обновить базу":
        admin_list = SETTINGS['admin_list']
        if message.from_user.id in admin_list:
            try:
                carTable.update()
                bot.send_message(message.chat.id, "База успешно обновлена")
            except Exception as err:
                bot.send_message(message.chat.id, f"Ошибка обновления базы:\n{err}")
        else:
            bot.send_message(message.chat.id, "Доступ запрещен")

    # Пользователь выбирает регион
    elif user_data['stage'] == STAGE_ZERO:
        if (text in carTable.brands.keys()):
            user_data['stage'] = STAGE_REGION_CHOSEN
            user_data['region'] = text

            markup = brand_menu_markup(text)
            bot.send_message(message.chat.id, f"Выберите марку автомобиля", reply_markup=markup)

    # Пользователь выбирает бренд
    elif user_data['stage'] == STAGE_REGION_CHOSEN: 
        if text in carTable.brands[user_data['region']]:
            user_data['stage'] = STAGE_BRAND_CHOSEN
            user_data["brand"] = text

            # Создаем клавиатуру для выбора модели или всех моделей
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("⬅️ Назад"))
            markup.add(types.KeyboardButton("📄 Все модели"))        
            models = {car.model for car in carTable.cars if car.brand == text}
            for model in models:
                markup.add(types.KeyboardButton(model))
            bot.send_message(message.chat.id, f"Выберите модель или все модели", reply_markup=markup)

    elif user_data['stage'] == STAGE_BRAND_CHOSEN:
        if text == "📄 Все модели":
            chosen_brand = user_data['brand']  
            car_n = 1
            for car in carTable.cars:
                if car.brand == chosen_brand:
                    car_name = car.model
                    car_years = car.data[3]
                    car_compl = car.configuration
                    msg_head = f"{car_n}) <b>{car.brand} {car_name} {car_years} {car_compl}</b>"
                    msg_body = list()
                    for idx in range(5, len(carTable.columns)):
                        msg_body.append(f"<code>{carTable.columns[idx]}</code>: <b>{car.data[idx]}</b>")
                    msg_body = "\n".join(msg_body)
                    bot.send_message(message.chat.id, f"{msg_head}\n{msg_body}", parse_mode="HTML")
                    car_n += 1

        elif any(text == car.model for car in carTable.cars):
            # Пользователь выбрал конкретную модель
            chosen_model = text
            chosen_brand = user_data['brand']
            car_n = 1
            for car in carTable.cars:
                if car.brand == chosen_brand and car.model == chosen_model:
                    car_name = car.model
                    car_years = car.data[3]
                    car_compl = car.configuration
                    msg_head = f"{car_n}) <b>{car.brand} {car_name} {car_years} {car_compl}</b>"

                    msg_body = list()
                    for idx in range(5, len(carTable.columns)):
                        msg_body.append(f"<code>{carTable.columns[idx]}</code>: <b>{car.data[idx]}</b>")
                    msg_body = "\n".join(msg_body)

                    bot.send_message(message.chat.id, f"{msg_head}\n{msg_body}", parse_mode="HTML")
                    time.sleep(0.1)
                    car_n += 1

    user_data['last_action_date'] = get_date_str()
    db.update(USERS_TABLE, user_data)

# Запуск бота
def bot_start(): 
    while True:
        try:
            logger.info("Start polling")
            bot.polling(non_stop=True, interval=1, timeout=50)
        except Exception as err:
            error_chain = traceback.format_exc()
            logger.fatal(f"Error chain:\n{error_chain}\n")
            logger.info("Restart in 2 sec")
            time.sleep(2)
