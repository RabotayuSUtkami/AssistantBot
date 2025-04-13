import telebot
from telebot import types
from pyowm import OWM
from pyowm.utils import config as cfg

from geopy.geocoders import Nominatim

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
itembtn2 = types.KeyboardButton('v')
itembtn3 = types.KeyboardButton('d')
#markup.add(itembtn1, itembtn2, itembtn3)
markup.add(itembtn1)



def getWeather(place):  # получать город из бд
    observation = mgr.weather_at_place('Набережные Челны')
    w = observation.weather
    print(w.detailed_status)         # 'clouds'
    print(w.wind()       )           # {'speed': 4.6, 'deg': 330}
    print(w.humidity    )            # 87
    print("temperature: ", w.temperature('celsius')['temp'])  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
    print(w.rain       )             # {}
    print(w.heat_index)              # None
    print(w.clouds   )               # 75


    

@bot.message_handler(commands=['start'])
def send_welcome(message):
    #bot.reply_to(message, "Howdy, how are you doing?") # ответ на сообщение
    bot.send_message(message.chat.id, 'Hi', reply_markup=markup)


@bot.message_handler(content_types=['location'])
def handle_messages(messages):
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
    getWeather(place)

@bot.message_handler(content_types=['text'])

def handle_messages(messages):
    print(messages)
    if messages.text == "Привет":
        
        bot.send_message(messages.chat.id, 'privet')

bot.infinity_polling()
