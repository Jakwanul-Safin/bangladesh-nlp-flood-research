from unidecode import unidecode
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import json
from uuid import uuid4
import time

def dailyStarArchiveLinks(soup):

    links = soup.findAll('div', {'class':['panel-pane', 'pane-news-col']})
    links2 = []
    for i,l in enumerate(links):
        if i<2: continue
        for a in l.findAll('a'):
            if a:
                href = a['href']
                if 'https://www.thedailystar.net' not in href: href = 'https://www.thedailystar.net' + href
                links2.append(href)
    return links2

def get_soup(site, selenium=False):
    if selenium:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(executable_path='/Applications/chromedriver', options=options)
        driver.get(site)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # open('trial.html','w').write(driver.page_source)
    else:
        page = requests.get(site)
        soup = BeautifulSoup(page.text, 'html.parser')
    return soup

def theDailyStarScrape(soup, site):
    datePublished = soup.find('meta', itemprop="datePublished")
    if datePublished: datePublished = datePublished['content']
    headline = soup.find('h1', itemprop='headline')
    if headline: headline = headline.text
    authors = soup.find('div', itemprop='author')
    if authors:
        authors2 = authors.find('span', itemprop='name')
        if authors2:
            authors3 = authors.find_all('a')
            if authors3:
                authors = [a.text for a in authors3]
            else:
                authors = authors.text
    text = soup.find('article', role='article')
    if text:
        textp = text.find_all('p')
        if textp: text = ' '.join([p.text for p in textp])

    if not text: text = ''
    if headline: headline = unidecode(headline)
    if text: text = unidecode(text)

    meta = {
        "link": site,
        "query_info": {
            "query": "dailyStarArchive",
            "paper": "theDailyStar",
            "date_range": []
        },
        'datePublished': datePublished
    }
    article = {
        'headline': headline,
        'authors': authors,
        'text': 'Date Published:{}      \n'.format(datePublished) + text
    }
    id = str(uuid4())

    return {
        'meta': meta,
        'article': article,
        'id': id
    }

def isLeap(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False

if __name__=='__main__':
    all_years = range(1998,2015)
    dates = []
    for i in all_years:
        count = 0
        innerMonth = []
        monthRange = 13
        if i == 2020: monthRange = 10
        for months in range(1, monthRange):
            day_range = 31 if months in [1, 3, 5, 7, 8, 10, 12] else 30
            if months == 2:
                if isLeap(i):
                    day_range = 29
                else:
                    day_range = 28
            for day in range(1, day_range + 1):
                key = str(i) + '-' + '{:02d}'.format(months) + '-' + '{:02d}'.format(day)
                dates.append(key)
    data = json.load(open('../paper_data/thedailystar/theDailyStar3_data.json'))
    currectDates = [str(d['meta']['datePublished']).split('T')[0] for d in data]
    for c in currectDates:
        if c in dates:
            dates.remove(c)
    print('Total Dates left:',len(dates))
    # print(sorted(dates, key=lambda x:x.split('-')))

    for i,date in enumerate(dates):
        site = 'https://www.thedailystar.net/newspaper?date={}'.format(date)

        soup = get_soup(site)
        links = dailyStarArchiveLinks(soup)
        links = set(links)
        if not links:
            meta = {
                "link": '',
                "query_info": {
                    "query": "dailyStarArchive",
                    "paper": "theDailyStar",
                    "date_range": []
                },
                'datePublished': date
            }
            article = {
                'headline': '',
                'authors': '',
                'text': ''
            }
            id = str(uuid4())
            data.append({
                'meta': meta,
                'article': article,
                'id': id
            })
        for l in links:
            try:
                data.append(theDailyStarScrape(get_soup(l),l))
            except Exception as e:
                print('\n',l)
        if i%5 == 0:
            print('.-',end = '')
            json.dump(data, open('../paper_data/thedailystar/theDailyStar3_data.json', 'w'), indent=2)
    json.dump(data, open('../paper_data/thedailystar/theDailyStar3_data.json', 'w'), indent=2)
