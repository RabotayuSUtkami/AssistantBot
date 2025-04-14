import time

import telebot
from telebot import types
from pyowm import OWM
from pyowm.utils import config as cfg

from geopy.geocoders import Nominatim

import sqlite3
import schedule
import threading



token = open("token.txt", 'r').read()
bot = telebot.TeleBot(token)
owmToken = open("OWMtoken.txt", 'r').read()

config = cfg.get_default_config()
config['language'] = 'ru'
owm = OWM(owmToken, config)
mgr = owm.weather_manager()



markup = types.ReplyKeyboardMarkup(row_width=2)
itembtn1 = types.KeyboardButton('Отправить адрес' ,request_location = True)
itembtn2 = types.KeyboardButton('Нет')
itembtn3 = types.KeyboardButton('d')
#markup.add(itembtn1, itembtn2, itembtn3)
markup.add(itembtn1, itembtn2)






def getWeather(userid):
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

    print(w.detailed_status)
    print(w.wind())
    print(w.humidity)
    print("temperature: ", w.temperature('celsius')['temp'])
    print(w.rain)
    print(w.heat_index)
    print(w.clouds)


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
    except:
        place = locname.raw['address']['municipality']

    bot.send_message(messages.chat.id, f'Ваше местоположение получено. Город: {place}')

    cursor.execute(f'SELECT location FROM users WHERE userId = {messages.chat.id}')
    results = cursor.fetchall()

    for row in results:
        if row[0] != place:
            cursor.execute('UPDATE users SET location = ? WHERE userId = ?', (place, messages.chat.id))
            connection.commit()

    connection.close()
    getWeather(messages.chat.id)

@bot.message_handler(content_types=['text'])

def handle_messages(messages):
    print(messages)
    if messages.text == "Привет":
        
        bot.send_message(messages.chat.id, 'privet')



def notification():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute(f'SELECT userId FROM users')
    results = cursor.fetchall()

    for row in results:
        userid = row[0]
        getWeather(userid)

    connection.close()

def checkTime():

    schedule.every().day.at('06:00').do(notification)

    while True:
        schedule.run_pending()
        time.sleep(59)


#bot.infinity_polling()



if __name__ == '__main__':
    t1 = threading.Thread(target=bot.infinity_polling)
    t2 = threading.Thread(target=checkTime)
    t1.start()
    t2.start()
    t1.join()
    t2.join()