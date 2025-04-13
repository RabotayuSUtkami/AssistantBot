import telebot
from telebot import types
from pyowm import OWM
from pyowm.utils import config as cfg

from geopy.geocoders import Nominatim

import sqlite3




token = open("token.txt", 'r').read()
bot = telebot.TeleBot(token)
owmToken = open("OWMtoken.txt", 'r').read()

config = cfg.get_default_config()
config['language'] = 'ru'
owm = OWM(owmToken, config)
mgr = owm.weather_manager()



markup = types.ReplyKeyboardMarkup(row_width=2)
itembtn1 = types.KeyboardButton('Отправить адрес' ,request_location = True)
#types.KeyboardButton
itembtn2 = types.KeyboardButton('Нет')
itembtn3 = types.KeyboardButton('d')
#markup.add(itembtn1, itembtn2, itembtn3)
markup.add(itembtn1, itembtn2)



def getWeather(userid):  # получать город из бд

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT location FROM users WHERE userId  = {userid}')
    results = cursor.fetchall()

    for row in results:
        place = row[0]
        print(row)


    observation = mgr.weather_at_place(place)
    w = observation.weather

    weather = w.detailed_status
    windSpeed = w.wind()['speed']
    windHeading = '??' #w.wind_direction
    humidity = w.humidity
    temp = w.temperature('celsius')['temp']

    weatherText = f'''На улице: {weather}
Скорость ветра {windSpeed} м/с, {windHeading}
Температура воздуха {temp}°C, влажность {humidity}%
    '''
    bot.send_message(userid, weatherText)

    print(w.detailed_status)         # 'clouds'
    print(w.wind()       )           # {'speed': 4.6, 'deg': 330}
    print(w.humidity    )            # 87
    print("temperature: ", w.temperature('celsius')['temp'])  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
    print(w.rain       )             # {}
    print(w.heat_index)              # None
    print(w.clouds   )               # 75


def requestLocation(messages):
    if messages.text == "Отправить адрес":
        bot.send_message(messages.chat.id, 'ye')
    elif messages.text == "Нет":
        bot.send_message(messages.chat.id, 'no')



@bot.message_handler(commands=['start'])
def send_welcome(message):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT userId FROM users WHERE userId = {message.chat.id}')
    results = cursor.fetchall()

    if results == []:
        cursor.execute('INSERT INTO users (userId, userName, firstName, location) VALUES (?, ?, ?, ?)',
                       (message.chat.id, message.chat.username, message.chat.first_name, 'None'))
        connection.commit()

    #bot.reply_to(message, "Howdy, how are you doing?") # ответ на сообщение
    bot.send_message(message.chat.id, 'Хотите ли Вы получать прогноз погоды по Вашему местоположению?', reply_markup=markup)
    connection.close()
    #mesg = bot.send_message(message.chat.id, 'Хотите ли Вы получать прогноз погоды по Вашему местоположению?', reply_markup=markup)
    #bot.register_next_step_handler(mesg, requestLocation)


@bot.message_handler(content_types=['location'])
def handle_messages(messages):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    rawlatlng = messages.location
    latlng = f"{rawlatlng.latitude}, {rawlatlng.longitude}"
    
    geoLoc = Nominatim(user_agent="GetLoc")
    locname = geoLoc.reverse(latlng, language='ru')

    try:
        place = locname.raw['address']['city']
        #print(place)
    except:
        place = locname.raw['address']['municipality']
        #print(place)

    bot.send_message(messages.chat.id, f'Ваше местоположение получено. Город: {place}')

    cursor.execute(f'SELECT location FROM users WHERE userId = {messages.chat.id}')
    results = cursor.fetchall()

    for row in results:
        if row[0] != place:
            cursor.execute('UPDATE users SET location = ? WHERE userId = ?', (place, messages.chat.id))
            connection.commit()
        #print(row)

    connection.close()
    getWeather(messages.chat.id)

@bot.message_handler(content_types=['text'])

def handle_messages(messages):
    print(messages)
    if messages.text == "Привет":
        
        bot.send_message(messages.chat.id, 'privet')

bot.infinity_polling()

