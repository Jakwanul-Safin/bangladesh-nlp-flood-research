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

def newAgeScrape(soup, meta):
    headline, text = None, ''
    headlineMain = soup.find('div', class_='postInnerTopIn')
    if headlineMain: headline = headlineMain.find('h3')
    if headline: headline = headline.text.strip()

    textmain = soup.find('div', class_='postPageTestIn')
    if textmain:
        textp = textmain.find_all('p')
        if textp: text = ' '.join([p.text.strip() for p in textp])

    datePublished = None
    if headlineMain:
        datePublished2 = headlineMain.find_all(text=re.compile('Published', re.IGNORECASE))

        if datePublished2:
            datePublished2 = datePublished2[0]
            datePublished2 = datePublished2.split('|')
            if len(datePublished2)>1:
                datePublished2 = datePublished2[1].strip().split(',')
                if len(datePublished2)>1: datePublished = ' '.join(datePublished2[1:])
    if datePublished: datePublished = str(parse_date(datePublished))

    if headline: headline = unidecode(headline)
    if text: text = unidecode(text)

    return {
        'headline': headline,
        'datePublished': datePublished,
        'text': 'Date Published:{}      \n'.format(datePublished or meta['datePublished'])+text,

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
    site = 'https://www.newagebd.net/article/2614/ring-roads-planned-to-cut-tailbacks-in-dhaka'
    meta = {'datePublished':'TRIAL'}
    soup = get_soup(site)
    print(newAgeScrape(soup, meta))
