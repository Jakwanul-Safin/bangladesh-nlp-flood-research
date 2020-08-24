from unidecode import unidecode
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from datetime import datetime
from datefinder import find_dates
import re

def parse_date(date_obj):
    if not date_obj: return None
    elif type(date_obj)==datetime:
        return date_obj
    else:
        dates = [f for f in find_dates(date_obj)]
        if dates: return dates[0]
    return None

def dailyObserverScrape(soup, meta):
    # print(soup)
    # main_div = soup.find('div')
    # print(main_div.find('article'))
    # print(main_div.find('article').get_text())

    headline, text = None, ''
    headline = soup.find('div', class_='detail_heading')
    if headline: headline = headline.text.strip()

    textmain = soup.find('div', id=['newsDtl','f'])
    textp = textmain.find_all('p')
    if textp: text = ' '.join([p.text for p in textp if 'photo:' not in p.text.lower()])
    if not text: text = textmain.text.strip()

    datePublished = soup.find_all('span', text=re.compile('Published', re.IGNORECASE))
    if datePublished:
        datePublished2 = datePublished[0].getText()
        if datePublished2:
            datePublished2 = datePublished2.split(':')
            if len(datePublished2)>1:
                datePublished = datePublished2[1]
    if datePublished: datePublished = str(parse_date(datePublished))

    if headline: headline = unidecode(headline)
    if text: text = unidecode(text)

    return {
        'headline': headline,
        'datePublished': datePublished,
        'text': 'Date Published:{}      \n'.format(meta['datePublished'])+text
    }

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

if __name__=='__main__':
    site = 'https://www.observerbd.com/details.php?id=72468'
    # site = 'https://www.observerbd.com/2014/09/06/41457.php'
    meta = {'datePublished':'TRIAL'}
    soup = get_soup(site)
    print(dailyObserverScrape(soup, meta))
