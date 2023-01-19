import datetime
import random
import time
import telebot
import requests as req
from geopy.geocoders import Nominatim
from telebot import types
from bs4 import BeautifulSoup as bs
from googletrans import Translator

# APIs
WeatherApi = "API"
bot = telebot.TeleBot("API")
RIA = 'https://t.me/s/rian_ru'
MASH = 'https://t.me/s/breakingmash'
BBS = 'https://www.telegram.me/s/bbcrussian'

# Weather
weather_emoji = {
    "Clear": "☀",
    "Clouds": "☁",
    "Rain": "🌧",
    "Thunderstorm": "🌩",
    "Snow": "🌨️",
}

conditions = {
    "Clear": "Ясно",
    "Clouds": "Облачно",
    "Rain": "Дождь",
    "Thunderstorm": "Гром",
    "Snow": "Снег",
}

loc = None


@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        global loc
        loc = (message.location.latitude, message.location.longitude)


def city_search(loc):
    geolocator = Nominatim(user_agent="Tra-bot")
    adr = geolocator.reverse(loc)
    adr = adr.raw['address']
    city = adr.get('city')
    print(city)
    return city


# News
def get_news(ag):
    n = req.get(ag)
    pn = bs(n.text, 'html.parser')
    news = pn.findAll('div', class_="tgme_widget_message_text js-message_text")
    news = [i.text for i in news]
    time = pn.findAll('a', class_="tgme_widget_message_date")
    time = [i.text for i in time]
    nn = random.randint(-1, len(news))
    return (f"{time[nn]}\n"
            f"{news[nn]}.")


# Translate
def translate(text):
    trans = Translator()
    text = trans.translate(str(text), dest='fr')
    return text


# Telegram
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """Введите одну из следующих команд:
/weather - Погода.
/news - Новости.
/translator - Переводчик.
    """)


@bot.message_handler(commands=['weather'])
def weather(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    if loc is None:
        bot.send_message(message.chat.id,
                         "Для корректной выдачи прогноза отправьте свою геолокацию.",
                         reply_markup=keyboard)
        time.sleep(8)
        while loc is None:
            bot.send_message(message.chat.id,
                             "Для корректной выдачи прогноза отправьте свою геолокацию.",
                             reply_markup=keyboard)
            time.sleep(8)
    city = city_search(loc)
    r = req.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WeatherApi}&units=metric"
    )
    data = r.json()
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    sunset = str(datetime.datetime.fromtimestamp((data["sys"]["sunset"])))
    wt = data["weather"][0]["main"]
    if wt in weather_emoji:
        wej = weather_emoji[wt]
        if wt == "Clear" and datetime.datetime.now().hour > int(sunset[11] + sunset[12]):
            wej = "🌕"
    else:
        wej = None
    bot.send_message(message.chat.id, f"Погода на {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                                      f"{city}.\n"
                                      f"Погода: {conditions[wt]}\n"
                                      f"Температура: {temp}°C\n"
                                      f"Влажность: {humidity}%\n"
                                      f"Скорость ветра: {wind}м/с\n", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, wej)


@bot.message_handler(commands=['news'])
def news(message):
    newsRIA = get_news(RIA)
    newsMASH = get_news(MASH)
    newsBBS = get_news(BBS)
    bot.send_message(message.chat.id, f"РИА Новости:\n"
                                      f"{newsRIA}\n"
                                      f"\nMash News:\n"
                                      f"{newsMASH}\n"
                                      f"\nBBS Russia:\n"
                                      f"{newsBBS}")


@bot.message_handler(commands=['translator'])
def translator(message):
    bot.send_message(message.chat.id, "Введите исходный текст.")

@bot.message_handler()
def st(message):
    text = message.text
    text = translate(text)
    bot.send_message(message.chat.id, text.text)


bot.polling(none_stop=True)