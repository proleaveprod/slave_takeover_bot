import telebot, time, os, json
from google_sheets import carTable
from telebot import types

bot_configs = dict()
with open('settings\\settings.json', 'r', encoding='utf-8') as file:
    bot_configs = json.load(file)



# Путь к файлу для сохранения данных пользователей
USER_DATA_FILE = 'settings\\user_data.json'

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

    bot.send_message(message.chat.id, "Выберите регион производителя", reply_markup=markup)

# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text

    if text in carTable.brands.keys():
        # Пользователь выбрал регион
        region = text
        user_data[user_id] = {"region": region}
        save_user_data(user_data)

        # Создаем клавиатуру с брендами для выбранного региона
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for brand in carTable.brands[region]:
            markup.add(types.KeyboardButton(brand))

        # Кнопка "Назад"
        markup.add(types.KeyboardButton("Назад"))

        bot.send_message(message.chat.id, f"Выберите марку автомобиля", reply_markup=markup)

    elif any(text in carTable.brands[region] for region in carTable.brands.keys()):
        # Пользователь выбрал марку автомобиля
        chosen_brand = text
        user_data[user_id]["brand"] = chosen_brand
        save_user_data(user_data)

        print(f"Request from user({user_id}):{user_data[user_id]}")        
        car_n = 1
        for i in range(len(carTable.cars)):
            car = carTable.cars[i]
            
            if car.brand == chosen_brand:
                
                car_name = car.data[2]
                car_years = car.data[3]
                car_compl = car.data[4]
                msg_head = f"{car_n}) <b>{car.brand} {car_name} {car_years} {car_compl}</b>"
                
                msg_body = list()
                for idx in range(5,len(carTable.columns)):
                    msg_body.append(f"<i>{carTable.columns[idx]}</i>: <b>{car.data[idx]}</b>")
                msg_body = "\n".join(msg_body)


                bot.send_message(message.chat.id, f"{msg_head}\n{msg_body}",parse_mode="HTML")
                time.sleep(0.1)
                car_n+=1

    elif text == "Назад":
        start(message)

    elif text == "🛠 Обновить базу":

        admin_list = bot_configs.get('admin_list')
        if message.from_user.id in admin_list:
            try:
                carTable.update()
                bot.send_message(message.chat.id, f"База успешно обновлена")
                print(f"Base updated by user({message.from_user.id}): {len(carTable.cars)} cars")
            except Exception as err:
                bot.send_message(message.chat.id, f"Ошибка обновления базы:\n{err}")
                print(f"Error base update by user({message.from_user.id}):\n{err}")
        else:
            bot.send_message(message.chat.id, f"Доступ запрещен")
def bot_start():

    while True:
        # try:
            print("Bot polling is started")
            bot.polling(non_stop=True,interval=1,timeout=50)
        # except Exception as err:
        #     print(f"bot.polling() ERROR:\n{err}\n\n Restart in 5 sec")
        #     time.sleep(5)