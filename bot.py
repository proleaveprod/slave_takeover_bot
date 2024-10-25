import telebot, time, os, json
from google_sheets import carTable
from telebot import types
from file_logger import logger

# Чтение настроек
bot_configs = dict()
with open('settings/settings.json', 'r', encoding='utf-8') as file:
    bot_configs = json.load(file)

# Путь к файлу для сохранения данных пользователей
USER_DATA_FILE = 'settings/user_data.json'

# Загрузка данных о пользователях из файла
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохранение данных о пользователях в файл
def save_user_data(data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

user_data = load_user_data()

# Инициализация бота
bot = telebot.TeleBot(bot_configs['bot-telegram-token'])

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):    
    # Создаем клавиатуру с регионами
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    for region in carTable.brands.keys():
        markup.add(types.KeyboardButton(region))

    admin_list = bot_configs.get('admin_list')
    if message.from_user.id in admin_list:
        markup.add(types.KeyboardButton("🛠 Обновить базу"))

    if str(message.from_user.id) not in user_data.keys():
        logger.debug(f"Bot: New user {message.from_user.id}")


    bot.send_message(message.chat.id, "Выберите регион производителя", reply_markup=markup)

# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text

    logger.debug(f"Bot: {message.from_user.id} request: {text}")
    
    if text in carTable.brands.keys():
        # Пользователь выбрал регион
        region = text
        user_data[user_id] = {"region": region}
        save_user_data(user_data)

        # Создаем клавиатуру с брендами для выбранного региона
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        
        # Кнопка "Назад"
        markup.add(types.KeyboardButton("⬅️ Назад"))

        for brand in carTable.brands[region]:
            markup.add(types.KeyboardButton(brand))


        bot.send_message(message.chat.id, f"Выберите марку автомобиля", reply_markup=markup)

    elif any(text in carTable.brands[region] for region in carTable.brands.keys()):
        # Пользователь выбрал марку автомобиля
        chosen_brand = text
        user_data[user_id]["brand"] = chosen_brand
        save_user_data(user_data)

        
        # Создаем клавиатуру для выбора модели или всех моделей
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # Кнопка "Назад"
        markup.add(types.KeyboardButton("⬅️ Назад"))
        # Кнопка "Все модели"
        markup.add(types.KeyboardButton("📄 Все модели"))
        
        # Добавляем кнопки для всех моделей марки
        models = {car.model for car in carTable.cars if car.brand == chosen_brand}
        for model in models:
            markup.add(types.KeyboardButton(model))


        bot.send_message(message.chat.id, f"Выберите модель или все модели", reply_markup=markup)

    elif text == "📄 Все модели":
        # Пользователь выбрал "Все модели"
        chosen_brand = user_data[user_id].get("brand")

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
                time.sleep(0.1)
                car_n += 1

    elif any(text == car.model for car in carTable.cars):
        # Пользователь выбрал конкретную модель
        chosen_model = text
        chosen_brand = user_data[user_id].get("brand")

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

    elif text == "⬅️ Назад":
        start(message)

    elif text == "🛠 Обновить базу":
        admin_list = bot_configs.get('admin_list')
        if message.from_user.id in admin_list:
            try:
                carTable.update()
                bot.send_message(message.chat.id, "База успешно обновлена")
            except Exception as err:
                bot.send_message(message.chat.id, f"Ошибка обновления базы:\n{err}")
        else:
            bot.send_message(message.chat.id, "Доступ запрещен")
            logger.debug("Bot: Access denied")

# Запуск бота
def bot_start():
    while True:
        try:
            logger.info("Bot: Starting of the polling")
            bot.polling(non_stop=True, interval=1, timeout=50)
        except Exception as err:
            logger.error(f"Bot: Polling ERROR:\n{err}")
            logger.info("Bot: Restart in 5 second")
            time.sleep(5)
