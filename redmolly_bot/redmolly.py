#!C:\Python34\python.exe

"""
redmolly.py by Temur Pallaev, 26.01.2017
Simple bot for Telegram - says hello, returns random numbers (why?),
currencies, news, vacancies and weather.
Add: links to the news, prettify vacancies output
"""

# v. 1.4

import telepot
import time
import random
import requests
import urllib.parse
import urllib.request
import re
from bs4 import BeautifulSoup
import secret


def handle(msg):

    def parseme(url):
                headers = {}
                headers[
                    'User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
                req = urllib.request.Request(url, headers=headers)
                resp = urllib.request.urlopen(req)
                main_site = resp.read()
                soup = BeautifulSoup(main_site, 'html.parser')
                return soup

    chat_id = msg['from']['id']
    command = msg['text']
    whois = msg['from']['first_name']

    print('Got message: %s' % command)

    if command == '/hi':
        bot.sendMessage(chat_id, 'Hello, %s' % whois)

    elif command == '/random':
        rand_nums = []
        def lottery():
            for i in range(6):
                yield random.randint(1,40)
            yield random.randint(1,15)
        for i in lottery():
            rand_nums.append(i)
        bot.sendMessage(chat_id, rand_nums)

    elif command == '/currency':
        url1 = 'https://currency-api.appspot.com/api/EUR/USD.json'
        url2 = 'https://currency-api.appspot.com/api/USD/EUR.json'
        url3 = 'https://currency-api.appspot.com/api/USD/RUB.json'
        r1 = requests.get(url1)
        r2 = requests.get(url2)
        r3 = requests.get(url3)
        r1 = r1.json()['rate']
        r2 = r2.json()['rate']
        r3 = r3.json()['rate']
        bot.sendMessage(chat_id, 'EUR to USD -> ' + str(r1))
        bot.sendMessage(chat_id, 'USD to EUR -> ' + str(r2))
        bot.sendMessage(chat_id, 'USD to RUB -> ' + str(r3))

    elif command == '/news':
        soup = parseme('https://news.tj/')
        all_news = soup.find("div", class_="news-block-container")
        titles = all_news.find_all('p')
        for title in titles:
            bot.sendMessage(chat_id, title.text)

    elif command == '/vacancies':
        soup = parseme('http://somon.tj/vakansii/it--telekom--kompyuteryi')
        containers = soup.find_all("div", class_="announcement-container")
        vacancies = []
        for container in containers:
            vacancies.append({
                'title': container.find("a", class_="name").text.strip(),
                'date': container.find("p", class_="float-left").text,
                'price': container.find("p", class_="price").text.strip(),
                'link': "http://somon.tj" + container.find(href=re.compile("adv"))['href']
                })
        for vacancy in vacancies[:5]:
            bot.sendMessage(chat_id, str(vacancy))

    elif command == '/weather':
            weather_api_key = secret.WEATHER_API_KEY
            api_call = 'http://api.openweathermap.org/data/2.5/find?q=Dushanbe&units=metric&appid=' + weather_api_key
            request_from_weather_api = requests.get(api_call)
            data_from_api = request_from_weather_api.json()['list']
            data = {}
            weather = {}
            for i in data_from_api:
                data.update(i)
            for y in data['weather']:
                weather.update(y)
            weather_output = '{} in {}. Temperature is {} C.'.format(weather['description'], data['name'], data['main']['temp'])
            bot.sendMessage(chat_id, weather_output)

bot = telepot.Bot(secret.KEY)
bot.notifyOnMessage(handle)
print('I am listening ...')

while 1:
    time.sleep(10)
