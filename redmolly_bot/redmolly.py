#!C:\Python34\python.exe

"""
redmolly.py by Temur Pallaev, 26.01.2017
Simple bot for Telegram - says hello, returns random numbers (why?),
currencies, news, vacancies and weather.
Add: links to the news, prettify vacancies output
"""

# v. 1.7

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
    # this function parses given url and returns data in soup var. Here I use two tools to
    # parse website - urllib (old, commented) and requests (new one).
    def parseme(url):
        headers = {}
        headers[
            'User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        # req = urllib.request.Request(url, headers=headers)
        # resp = urllib.request.urlopen(req)
        # main_site = resp.read()
        # soup = BeautifulSoup(main_site, 'html.parser')
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup

    # this chunk provides output for debugging purposes
    chat_id = msg['from']['id']
    command = msg['text']
    whois = msg['from']['first_name']

    print('Got message: %s' % command)

    # from here I begin to declare and code commands users can send to the bot
    # and code bot's reaction respectively
    #
    # first one is simple - bot responses with greetings, and uses user's name in it.
    if command == '/hi':
        bot.sendMessage(chat_id, 'Hello, %s' % whois)

    # yielding random numbers - for the sake of curiosity
    elif command == '/random':
        rand_nums = []

        def lottery():
            for x in range(6):
                yield random.randint(1, 40)
            yield random.randint(1, 15)

        for i in lottery():
            rand_nums.append(i)
        bot.sendMessage(chat_id, rand_nums)

    # this command uses external api to parse currencies rate
    elif command == '/currency':
        url1 = 'https://currency-api.appspot.com/api/EUR/USD.json'
        url2 = 'https://currency-api.appspot.com/api/USD/EUR.json'
        url3 = 'https://currency-api.appspot.com/api/USD/RUB.json'

        # Need to style 9 lines below. Use loops
        r1 = requests.get(url1)
        r2 = requests.get(url2)
        r3 = requests.get(url3)
        r1 = r1.json()['rate']
        r2 = r2.json()['rate']
        r3 = r3.json()['rate']
        bot.sendMessage(chat_id, 'EUR to USD -> ' + str(r1))
        bot.sendMessage(chat_id, 'USD to EUR -> ' + str(r2))
        bot.sendMessage(chat_id, 'USD to RUB -> ' + str(r3))

    # this chunk uses parseme function form above, gets and scrapes last news titles from news.tj
    # Here I need to add link to the news for better UX
    elif command == '/news':
        soup_news = parseme('https://news.tj/')
        all_news = soup_news.find("div", class_="news-block-container")
        titles = all_news.find_all('p')
        for title in titles:
            bot.sendMessage(chat_id, title.text)

    # part that I keep stumbling on. Again, uses parse function.
    # Firstly, I scraped data from somon.tj, but it seems like they changed their html a bit,
    # so it do not outputs full info, only vacancies title. Thus, somon.tj part commented out for a while.
    # Now this part scrapes untj.org website for vacancies. Need to add links to the vacancies.
    elif command == '/vacancies':
        # soup = parseme('http://somon.tj/vakansii/it--telekom--kompyuteryi')
        # containers = soup.find_all("div", class_="announcement-container")
        # vacancies = []
        # for container in containers:
        #     vacancies.append({
        #         'title': container.find("a", class_="announcement-block__title").text.strip(),
        #         'date': container.find("p", class_="time-like"),
        #         'price': container.find("p", class_="list-announcement-block__price"),
        #         #'link': "http://somon.tj" + container.find(href=re.compile("adv"))['href']
        #         })
        #         for vacancy in vacancies[:5]:
        #             bot.sendMessage(chat_id, str(vacancy))

        url_untj = 'http://www.untj.org/index.php?option=com_flexicontent&view=category&cid=89:local-vacancies&Itemid=514'
        soup_untj = parseme(url_untj)
        titles_list = []
        table = soup_untj.find('table', class_="flexitable")
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            titles_list.append([ele for ele in cols if ele])

        # titles_list.insert(0, 'Detailed information on positions ' + url)
        bot.sendMessage(chat_id, 'Vacancies from untj.org \n'
                                 'Visit ' + url_untj + ' for details')

        for item in titles_list[:8]:
            bot.sendMessage(chat_id, str(item))

    # This chunk uses external weather API. Nothing new in here.
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
        weather_output = '{} in {}. Temperature is {} C.'.format(weather['description'], data['name'],
                                                                 data['main']['temp'])
        bot.sendMessage(chat_id, weather_output)


# This piece of code provides bot's secret key.
bot = telepot.Bot(secret.KEY)
bot.notifyOnMessage(handle)
print('I am listening ...')

while 1:
    time.sleep(10)
